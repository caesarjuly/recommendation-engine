from typing import Dict, Text
import tensorflow as tf
import tensorflow_recommenders as tfrs
from trainer.models.common.feature_cross import MultiHeadSelfAttentionLayer
from trainer.models.common.basic_layers import DNNLayer

from trainer.util.tools import ObjectDict


class AutoInt(tfrs.Model):
    def __init__(
        self, hparams: ObjectDict, deep_emb: tf.keras.Model, wide_emb: tf.keras.Model
    ):
        super().__init__()
        self.deep_emb = deep_emb
        self.wide_emb = wide_emb
        self.hparams = hparams
        self.task: tf.keras.layers.Layer = tfrs.tasks.Ranking(
            loss=tf.keras.losses.BinaryCrossentropy(),
            metrics=[tf.keras.metrics.BinaryCrossentropy(), tf.keras.metrics.AUC()],
        )
        self.linear = tf.keras.experimental.LinearModel(
            kernel_regularizer=tf.keras.regularizers.l2(l2=0.001)
        )
        self.attentions = tf.keras.Sequential(
            [
                MultiHeadSelfAttentionLayer(
                    head_dim=hparams.head_dim, head_num=hparams.head_num
                )
                for _ in range(hparams.att_layer_num)
            ]
            + [tf.keras.layers.Flatten(), tf.keras.layers.Dense(1)]
        )
        self.deep = tf.keras.Sequential(
            [
                tf.keras.layers.Flatten(),
                DNNLayer(output_logits=True),
            ]
        )
        self.activation = tf.keras.layers.Activation("sigmoid")

    def call(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
        deep_emb = self.deep_emb(features)
        return self.activation(
            self.linear(self.wide_emb(features), training=training)
            + self.attentions(deep_emb, training=training)
            + self.deep(deep_emb, training=training),
        )

    def compute_loss(
        self, features: Dict[Text, tf.Tensor], training=False
    ) -> tf.Tensor:
        labels = tf.expand_dims(
            tf.where(features[self.hparams.label] > 3, 1, 0), axis=-1
        )
        rating_predictions = self(features, training=training)

        # The task computes the loss and the metrics.
        return self.task(
            labels=labels,
            predictions=rating_predictions,
            training=training,
        )

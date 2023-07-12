import tensorflow_recommenders as tfrs

from trainer.util.tools import Factory
from trainer.models.basic_ranker import *
from trainer.models.deepfm import *
from trainer.models.fm import *
from trainer.models.mask_net import *
from trainer.models.two_tower import *
from trainer.models.wide_and_deep import *
from trainer.models.features.movielens import *
from trainer.models.dcn import *
from trainer.models.xdeepfm import *
from trainer.models.autoint import *

model_factory = Factory()
model_factory.register_all_subclasses(tfrs.Model)

### Post scope experiments

In here we have experiments that go beyond the initial scope
of trying to imitate the method of UCLA and reproducing their
results.

These experiments are generally in two different categories:
 1. Experiments based on `UCLA_model_UCLA_dataset_without_visual_attributes.ipynb`
 2. Experiments that are a different approach to the setup.



##### Implemented
The experiments that are thought to be here, are represented
by inidividual notebooks with the following ideas:

- [X] Using initial training with search engine results
- [X] Other base network than resnet (Xception)
- [X] Other base network than resnet (Densenet)
- [X] ~~Changing output neuron (linear)~~
- [X] Add fully connected layers at the end + dropout
- [X] Reduce resizing (data augmentation)
- [X] Optimizers (using Adam instead of SGD)
- [X] Freeze the first _m_ layers (First 5 conv layers)
- [X] Experiment without any auxilliary tasks
- [X] Experiment without protest label but with visual attributes
- [X] Experiment with two FC layers and dropout, one for each task
- [X] Experiment training the network first on auxilliary tasks and then on the main task
- [X] Experiment training the network on multitask and then on only main task
- [X] Freeze all layers of ResNet
- [X] All frozen layers of ResNet and fully connected layer with .5 dropout
- [X] Fully connected for each multitask and reduced transform
- [X] Fully connected for each multitask and reduced transform while using both protest and visual attributes

##### Running

- [ ] All frozen layers of ResNet and fully connected layer with .5 dropout
- [X] Fully connected for each multitask and reduced transform
- [X] Fully connected for each multitask and reduced transform while using both protest and visual attributes

##### Completed before removing learning rate bug

- [ ] ~~Using initial training with search engine results~~
- [ ] ~~Other base network than resnet (Xception)~~
- [ ] ~~Other base network than resnet (Densenet)~~
- [ ] ~~Changing output neuron (linear)~~
- [X] [Add fully connected layers at the end + dropout](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_ADD_FC_DROPOUT_evaluation.png)
- [X] [Reduce resizing (data augmentation)](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_reduced_augmentation_evaluation.png)
- [X] [Optimizers (using Adam instead of SGD)](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_adam_optimizer_evaluation.png)
- [X] [Freeze the first _m_ layers (First 5 conv layers)](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_freeze_m_evaluation.png)
- [X] [Experiment without any auxilliary tasks](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_no_auxilliary_tasks_evaluation.png)
- [ ] ~~Experiment without protest label but with visual attributes~~

##### Completed after removing learning rate bug

- [X] [Original UCLA without visual attributes](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_UCLA_dataset_without_visual_attributes_evaluation.png)
- [X] [Using initial training with search engine results](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/search_engine_images_model_evaluation.png)
- [ ] ~~Other base network than resnet (Xception)~~
- [X] [Other base network than resnet (Densenet)](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/densenet_base_evaluation.png)
- [ ] ~~Changing output neuron (linear)~~
- [ ] ~~Add fully connected layers at the end + dropout~~
- [X] ~~Reduce resizing (data augmentation)~~
- [ ] ~~Optimizers (using Adam instead of SGD)~~
- [ ] ~~Freeze the first _m_ layers (First 5 conv layers)~~
- [X] ~~Experiment without any auxilliary tasks~~
- [X] [Experiment without protest label but with visual attributes](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_w_visual_attributes_no_protest_evaluation.png)
- [X] [Experiment with two FC layers and dropout, one for each task](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_ADD_FC_DROPOUT_EACH_TASK_evaluation.png)
- [X] [Experiment training the network first on auxilliary tasks and then on the main task](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_two_round_train_evaluation.png)
- [X] [Experiment training the network on multitask and then on only main task](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_two_round_train_multitask_evaluation.png)
- [X] [Freeze all layers of ResNet](https://github.itu.dk/lukl/Thesis_2018/raw/master/analysis/post_scope_experiments/plots/UCLA_model_freeze_all_evaluation.png)
- [X] All frozen layers of ResNet and fully connected layer with .5 dropout

##### Completed second iteration (combining experiments)
- [ ] Fully connected for each multitask and reduced transform
- [ ] Fully connected for each multitask and reduced transform while using both protest and visual attributes

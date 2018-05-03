### Post scope experiments

In here we have experiments that go beyond the initial scope
of trying to imitate the method of UCLA and reproducing their
results.

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
- [ ] Experiment training the network first on auxilliary tasks and then on the main task

These experiments are generally in two different categories:
 1. Experiments based on `UCLA_model_UCLA_dataset_without_visual_attributes.ipynb`
 2. Experiments that are a different approach to the setup.


##### Running

- [ ] Using initial training with search engine results
- [ ] ~~Other base network than resnet (Xception)~~
- [ ] Other base network than resnet (Densenet)
- [ ] ~~Changing output neuron (linear)~~
- [ ] Add fully connected layers at the end + dropout
- [ ] Reduce resizing (data augmentation)
- [ ] Optimizers (using Adam instead of SGD)
- [ ] Freeze the first _m_ layers (First 5 conv layers)
- [ ] Experiment without any auxilliary tasks
- [ ] Experiment without protest label but with visual attributes
- [ ] Experiment training the network first on auxilliary tasks and then on the main task


##### Completed before removing learning rate bug

- [ ] ~~Using initial training with search engine results~~
- [ ] ~~Other base network than resnet (Xception)~~
- [ ] ~~Other base network than resnet (Densenet)~~
- [ ] ~~Changing output neuron (linear)~~
- [X] Add fully connected layers at the end + dropout
- [X] Reduce resizing (data augmentation)
- [X] Optimizers (using Adam instead of SGD)
- [X] Freeze the first _m_ layers (First 5 conv layers)
- [X] Experiment without any auxilliary tasks
- [ ] ~~Experiment without protest label but with visual attributes~~

##### Completed after removing learning rate bug

- [X] Original UCLA without visual attributes
- [X] Using initial training with search engine results
- [ ] ~~Other base network than resnet (Xception)~~
- [X] Other base network than resnet (Densenet)
- [ ] ~~Changing output neuron (linear)~~
- [ ] ~~Add fully connected layers at the end + dropout~~
- [X] Reduce resizing (data augmentation)
- [ ] ~~Optimizers (using Adam instead of SGD)~~
- [ ] ~~Freeze the first _m_ layers (First 5 conv layers)~~
- [X] Experiment without any auxilliary tasks
- [X] Experiment without protest label but with visual attributes
- [X] Experiment with two FC layers and dropout, one for each task
- [ ] Experiment training the network first on auxilliary tasks and then on the main task

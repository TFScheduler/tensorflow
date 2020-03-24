TFScheduler/TensorFlow is a modified version of Tensorflow.
This fork is only suitable for building tensorflow-gpu.

## Build
```
$ git clone https://github.com/TFScheduler/tensorflow.git
$ cd tensorflow
$ ./configure 
$ bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package
$ ./bazel-bin/tensorflow/tools/pip_package/build_pip_package --gpu
```

## Run
rpc_server.py is needed for running TFScheduler/TensorFlow
```
python3 rpc_server.py
```

## License
...
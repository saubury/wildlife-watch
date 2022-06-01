  
# Credit
Much inspiration taken from https://github.com/tensorflow/examples/tree/master/lite/examples/object_detection/raspberry_pi


## Download the EfficientDet-Lite mode
```
curl     -L 'https://tfhub.dev/tensorflow/lite-model/efficientdet/lite0/detection/metadata/1?lite-format=tflite'     -o efficientdet_lite0.tflite
```


## Setup virtual python environment 
 ``` 
virtualenv -p `which python3` venv
source venv/bin/activate
python --version
pip --version
```

## Install requirements
```
  python3 -m pip install pip --upgrade
  python3 -m pip install -r requirements.txt
```

## Run
```
  python3 detect.py   --model efficientdet_lite0.tflite
```
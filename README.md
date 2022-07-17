# Citation
@inproceedings{yang2020multi,
  title={Multi-Scale Long Short-Term Memory Network with Multi-Lag Structure for Blood Glucose Prediction.},
  author={Yang, Tao and Wu, Ruikun and Tao, Rui and Wen, Shuang and Ma, Ning and Zhao, Yuhang and Yu, Xia and Li, Hongru},
  booktitle={KDH@ ECAI},
  pages={136--140},
  year={2020}
}

# Prerequisites
The code is designed to be run on the OhioT1DM Dataset.

# Preparation before operation
1. You need to use Excel to convert XML files from OhioT1DM Dataset into XLSX files.
2. You need to manually complete the "basal" list in the XLSX file. This is simple for people, they only need to complete it according to the information from the previous day.
3. After completing the above two steps, include the path of the XLSX file in the two YAML files in the experiments directory of the project.

# Install dependency libraries
You can install the required dependencies in bulk through requirements.txt.

# Reproduce final results
Just run the main.py file.

# Code reference declaration
https://github.com/johnmartinsson/blood-glucose-prediction

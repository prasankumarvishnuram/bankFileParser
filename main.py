import csv
import glob
import json
import os
from datetime import datetime, date

converted_data = []


def write_to_csv(dataFromBankFile, csvConfig, dataDetails, outputFile):
    
    with open(outputFile, 'w') as csv_file:
        header = []
        bankName = list(dataDetails.keys())[0]
        for field in csvConfig[bankName]["to_csv"]:
            header.append(field['name'])
        csv_output = csv.writer(csv_file)

        csv_output.writerow(header)

        for bankName in dataDetails.keys():
            for dict_fields in dataFromBankFile:
                data_list = []
                if bankName == dict_fields["bankName"]:
                    for field in csvConfig[bankName]["to_csv"]:
                        data_list.append(dict_fields[field['field']])
                    csv_output.writerow(data_list)


def read_csv_file(bankName, csvFile, configFile):
    with open(csvFile, encoding="utf-8-sig") as csv_file:
        csv_data = csv.DictReader(csv_file)
        for dict_data in csv_data:
            new_dict = {}
            for field in configFile[bankName]['fields']:
                name = field['name']
                csv_value = dict_data[name]
                new_dict["bankName"] = bankName
                try:
                    if field['type'] == 'int':
                        new_dict[name] = int(csv_value)
                    elif field['type'] == 'float':
                        new_dict[name] = float(csv_value)
                    elif field['type'] == 'date':
                        dt_temp = datetime.strptime(csv_value, field['format'])
                        new_dict[name] = date(dt_temp.year,
                                              dt_temp.month,
                                              dt_temp.day)
                    else:
                        new_dict[name] = csv_value
                except:
                    return None
            converted_data.append(new_dict)
    return converted_data


def load_json(json_file):
    with open(json_file) as f:
        data = json.load(f)

    return data


def convert(data, convert_to, bankName):
    for processData in data:
        if processData["bankName"] == bankName:
            for rule in convert_to:
                name = rule[1]
                if rule[0] == 'add':
                    processData[name] = processData[name] + rule[2]
                elif rule[0] == 'add_fields':
                    processData[name] = processData[name] + processData[rule[2]]
                elif rule[0] == 'divide':
                    processData[name] = processData[name] / rule[2]
                elif rule[0] == 'multiply':
                    processData[name] = processData[name] * rule[2]
                elif rule[0] == 'subtract':
                    processData[name] = processData[name] - rule[2]


if __name__ == '__main__':
    dataDetails = os.path.basename(file).split(".")[0]: file for file in glob.glob('input' + '/*.csv')
    configFileSpecification = "config.json"
    configFile = load_json(configFileSpecification)
    for bankName, csvFile in dataDetails.items():
        read_csv_file(bankName, csvFile, configFile)

    for bankName, csvFile in dataDetails.items():
        bank_info = configFile.get(bankName)
        if bank_info and 'convert' in bank_info:
            convert(converted_data, bank_info['convert'], bankName)
    write_to_csv(converted_data, configFile, dataDetails, "consolidatedCSV.csv")

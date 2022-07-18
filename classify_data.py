import os

from flask import Flask, jsonify
from constants import NAMES, SWISS_CITY
from dateutil.parser import parse
import boto3
import pymysql


app = Flask(__name__)
s3 = boto3.client("s3")
sns = boto3.client("sns")


def create_rds_connection():
    db = pymysql.connect(host="rdsdatabase.cvqlpnpjh6qk.ap-south-1.rds.amazonaws.com",
                         user="admin", password="admin123", port=3306)
    cursor = db.cursor()
    try:
        sql = """Create database rdsDB"""
        cursor.execute(sql)
        cursor.connection.commit()
    except Exception as e:
        pass
    sql = """Use rdsDB"""
    cursor.execute(sql)
    try:
        create_table = """CREATE TABLE IF NOT EXISTS view_message ( 
                            id INT AUTO_INCREMENT PRIMARY KEY, 
                            message VARCHAR(255) NOT NULL, 
                            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"""
        cursor.execute(create_table)
    except Exception as e:
        pass

    return cursor, db


@app.route('/<file_name>', methods=['GET'])
def home(file_name):
    try:
        s3.download_file(
            Bucket="swisscom-assignment-bucket", Key=file_name, Filename="data/{}".format(file_name)
        )
    except:
        return jsonify({"HTTP_STATUS":404, "message":"Unable to get file from S3 bucket"})
    if not os.listdir("data/"):
        os.mkdir("data/")
    with open(r"data/{}".format(file_name), 'r') as o:
        value = o.readlines()
    count = 0

    for val in value:
        all_word = val.replace("\n","").split(" ")
        for word in all_word:
            if word.lower() in SWISS_CITY:
                count += 1
            if word.lower() in NAMES:
                count += 1
            try:
                if parse(str(word), fuzzy=True):
                    count += 1
            except:
                pass
    if count > 0:
        message = "{} contains Sensitive Data".format(file_name)
    else:
        message = "{} contains Insensitive Data".format(file_name)
    try:
        cursor, db = create_rds_connection()
        query = """Insert into view_message(message) values("{}")""".format(message)
        cursor.execute(query)
        db.commit()
        cursor.close()
    except:
        return jsonify({"status":404, "message":"Unable to save data in RDS"})
    try:
        sns.publish(PhoneNumber="+917354642555", Message=message,
                    MessageAttributes={'AWS.SNS.SMS.SMSType': {'DataType': 'String', 'StringValue': 'Transactional'}})
    except:
        return jsonify({"status":404, "message":"Unable to send message"})

    return jsonify({"status":200,"message": message})

@app.route('/data', methods=['GET'])
def get_table_data():
    cursor, db = create_rds_connection()
    query = """select * from view_message"""
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify({"data": data})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

import pymysql.cursors
import csv
import sys

class mySQL(object):

    def connection(self):
        # 连接到数据库
        connection = pymysql.connect(host='localhost',
                                     port=3306,
                                     user='root',
                                     password='wuqiushan741826',
                                     db='GithubInfo',
                                     charset="utf8",
                                     cursorclass=pymysql.cursors.DictCursor)
        try:

            # with connection.cursor() as cursor:
            #     cursor.execute("INSERT INTO `PersonInfo` "
            #                    "(`TailURL`, `Email`, `Area`, `Like`, `Repositories`, `Stars`, `Followers`, `Following`, `Organize`, `PersonalURL`) "
            #                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            #                    ('beijing', 'wuqiush@163.com', 'bei', 'java', '23', '1', '2', '3', 'wq', 'com'))
            #     connection.commit()

            # with connection.cursor() as cursor:
            #     cursor.execute("DELETE FROM `study` WHERE `idstudy`=%s", '4')
            #     connection.commit()

            # with connection.cursor() as cursor:
            #     cursor.execute("update `study` set `name`=%s where `idstudy`=%s", ('wu', '4'))
            #     connection.commit()


            # with connection.cursor() as cursor:
            #     # Create a new record
            #     sql = "INSERT INTO `study` (`idstudy`, `name`, `age`) VALUES (%s, %s, %s)"
            #     cursor.execute(sql, ('1', '1webmaster@python.org', '30'))
            #
            # # connection is not autocommit by default. So you must commit to save
            # # your changes.
            # connection.commit()


            # with connection.cursor() as cursor:
            #     # Read a single record
            #     sql = "SELECT `idstudy`, `age` FROM `study` WHERE `age`=%s"
            #     cursor.execute(sql, ('30',))
            #     result = cursor.fetchone()
            #     print(result)

#'doubanFile.csv',

            pathArray = [
                'doubanFile10w.csv',
                'doubanFile2017-9-1.csv',
                'doubanFile2017-9-2.csv',
                'doubanFile2017-9-2.10.csv',
                'doubanFile2017-9-3.1.csv',
                'doubanFile2017-9-3.csv',
                'doubanFile2017-9-6.csv',
                'doubanFile2017-9-8.csv',
                          'doubanFile2017-9-9.csv',
                          'doubanFile2017-9-10.csv',
                          'doubanFile2017-9-11.csv']

            for element in pathArray:
                completeURL = '/Users/apple/Desktop/采集到的邮箱/' +  element
                print(completeURL)
                with open(completeURL) as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        tailURL = self.stringRemoveNull(row['Name'])
                        email = self.stringRemoveNull(row['Email'])
                        area = self.stringRemoveNull(row['Country'])
                        like = self.stringRemoveNull(row['Like'])
                        repositor = self.stringRemoveNull(row['Repositories'])
                        stars = self.stringRemoveNull(row['Stars'])
                        followers = self.stringRemoveNull(row['Followers'])
                        following = self.stringRemoveNull(row['Following'])
                        organize = self.stringRemoveNull(row['Organize'])
                        personURL = self.stringRemoveNull(row['PersonalURL'])
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute("INSERT INTO `GithubUserInfo` "
                                               "(`TailURL`, `Email`, `Area`, `Like`, `Repositories`, `Stars`, `Followers`, `Following`, `Organize`, `PersonalURL`) "
                                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                               (
                                                   tailURL, email, area, like, repositor, stars, followers, following,
                                                   organize,
                                                   personURL))
                                connection.commit()
                        except (TypeError, ValueError) as e:
                            print("错误123")
                            print(e)
                        except:
                            print("12")
        finally:
            print("重复项")
            #connection.close()

    def stringRemoveNull(self, oString):
        newString = str(oString).replace("\n", "")
        newString = newString.replace(" ", "")
        return  newString

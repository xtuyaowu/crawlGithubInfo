#coding=utf-8
'''
PyTools:PyCharm 2017.1
Python :Python3.5
Author :colby_chen
CreDate:2017-04-13
'''
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.selector import Selector
from douban.items import doubanItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError,TCPTimedOutError
import time
import pymysql.cursors
from douban.mysql import mySQL


class Douban(CrawlSpider):
    name = "doubanMovie"
    redis_key='douban:start_urls'
    recordURLString = ""  # 用来记录之前爬过的Follwing的链接
    followingStack = []  # ([("URL", "123"), ("URL1", "1.2k"), (), ...])
    errorCount = 0       # 错误统计
    oneTimeEnable = 0    # 出现多次错误时，去进去翻页

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
        "Referer": "https://github.com/"
    }

    def start_requests(self):

        myDB = mySQL()
        myDB.connection()

        # return [
        #     Request("https://github.com/login",
        #             meta={"cookiejar": 1},
        #             headers=self.headers,
        #             callback=self.parse_welcome)
        # ]

    def parse_welcome(self, response):
        print(response)
        token = Selector(response).xpath('//*[@id="login"]/form/div[1]/input[2]/@value').extract()[0]
        print(token)
        return FormRequest.from_response(
            response,
            meta={'cookiejar': response.meta['cookiejar']},
            formdata={"commit":"签到",
                      "utf8":"✓",
                      "authenticity_token": token,
                      "login": "576864273@qq.com",
                      "password": "wuqiushan741826"},
            callback=self.after_login,
            dont_filter = True,
        )

    #
    def after_login(self, response):
        return [
            Request("https://github.com/Simon57686",
                    meta={'cookiejar': response.meta['cookiejar']},
                    callback=self.gotoFollowing
                    )
        ]

    def gotoFollowing(self, response):
        return [
            Request(
                    # "https://github.com/Simon57686?tab=following",
                    # "https://github.com/naglis?tab=following",
                    "https://github.com/ostronom?tab=following",
                    meta={'cookiejar': response.meta['cookiejar']},
                    callback=self.gotoUser
                    )
        ]

    def gotoUser(self, response):
        try:
            selector = Selector(response)
            userUrlList = selector.xpath('//span[@class="link-gray pl-1"]/text()').extract()
            cycleCount = len(userUrlList)
            if cycleCount > 0:
                for item in userUrlList:
                    cycleCount = cycleCount - 1
                    itemUrl = "https://github.com/" + item
                    if cycleCount <= 3:
                        yield Request(itemUrl, meta={'cookiejar': response.meta['cookiejar']}, errback=self.errback,
                                      callback=lambda response, profileURL=itemUrl, preSelector=selector,
                                                      enable=True: self.getUserEmail(response, profileURL, preSelector,
                                                                                     enable))
                    else:
                        yield Request(itemUrl, meta={'cookiejar': response.meta['cookiejar']}, errback=self.errback,
                                      callback=lambda response, profileURL=itemUrl, preSelector=selector,
                                                      enable=False: self.getUserEmail(response, profileURL, preSelector,
                                                                                      enable))
            else:
                print(" cycleCount = ", cycleCount)
        except (TypeError, ValueError) as e:
            print("错误123")
            print(e)
        except:
            print("错误123T")


    def errback(self, failure):
        try:
            self.errorCount = self.errorCount + 1
            if self.errorCount >= 5:
                self.errorCount = 0
                print("出错次数过多--延时开始", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                time.sleep(600)
                print("出错次数过多--延时结束", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                self.oneTimeEnable = 10

            if failure.check(HttpError):
                yield self.error(failure.request.meta['task'], -1, 'error:HTTP错误 {0}'.format(failure.request.url))
            elif failure.check(DNSLookupError):
                yield self.error(failure.request.meta['task'], -1, 'error:DNS发生错误 {0}'.format(failure.request.url))
            elif failure.check(TimeoutError, TCPTimedOutError):
                yield self.error(failure.request.meta['task'], -1, 'error:超时 {0}'.format(failure.request.url))
            else:
                yield self.error(failure.request.meta['task'], -1, 'error:其他访问错误 {0}'.format(failure.request.url))
        except (TypeError, ValueError) as e:
            print("错误789")
            print(e)
        except:
            print("错误789T")


    def getUserEmail(self, response, profileURL, preSelector, enable):
        try:
            selector = Selector(response)
            profileSelector = selector.xpath('//*[@id="js-pjax-container"]/div/div[1]')
            navSelector = selector.xpath(
                '//div[@class="user-profile-nav js-sticky top-0"]//a[@class="underline-nav-item "]/span[@class="Counter"]/text()').extract()
            likeSelector = selector.xpath(
                '//div[@class="js-pinned-repos-reorder-container"]//p[@class="mb-0 f6 text-gray"]/text()').extract()
            likeString = ""
            for item in likeSelector:
                itemString = item.strip()
                if len(itemString) > 0:
                    if itemString in likeString:
                        print("")
                    elif len(likeString) == 0:
                        likeString += itemString
                    else:
                        likeString += "," + itemString
            item = doubanItem()
            item['Name'] = profileSelector.xpath(
                '//span[@class="p-nickname vcard-username d-block"]/text()').extract_first()
            item['Email'] = profileSelector.xpath('//li[@aria-label="Email"]/a/text()').extract_first()
            item['ProfileURL'] = profileURL
            item['Country'] = profileSelector.xpath('//span[@class="p-label"]/text()').extract_first()
            item['Organize'] = profileSelector.xpath('//span[@class="p-org"]/div/a/@href').extract_first()
            item['PersonalURL'] = profileSelector.xpath('//li[@aria-label="Blog or website"]/a/text()').extract_first()
            item['Repositories'] = navSelector[0]
            item['Stars'] = navSelector[1]
            item['Followers'] = navSelector[2]
            item['Following'] = navSelector[3]
            item['Like'] = likeString
            yield item
            # 判断是否要存入待爬队列里
            if profileURL in self.recordURLString:
                print("1234", profileURL)
            else:
                followingCount = navSelector[3].strip()
                followingCountAll = len(self.followingStack)
                if followingCountAll > 0:
                    preMaxFollwingString = self.followingStack[followingCountAll - 1][1]
                    if len(followingCount) > len(preMaxFollwingString):
                        self.followingStack.append((profileURL + "?tab=following", followingCount))
                    elif len(followingCount) > 3:
                        self.followingStack.append((profileURL + "?tab=following", followingCount))
                else:
                    self.followingStack.append((profileURL + "?tab=following", followingCount))
            if len(self.followingStack) > 10:
                del self.followingStack[0]
            if enable or self.oneTimeEnable > 0:
                if self.oneTimeEnable > 0:
                    if len(self.followingStack) > 0:
                        print("换新页")
                        maxFloowingURL = self.followingStack.pop()[0]
                        self.recordURLString += " " + maxFloowingURL
                        yield Request(maxFloowingURL, meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.gotoUser)
                    else:
                        print("停止")
                        if navSelector[3] > 0:
                            changeURL = profileURL + "?tab=following"
                            yield Request(changeURL, meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.gotoUser)
                        else:
                            print("未处理")
                self.oneTimeEnable = self.oneTimeEnable - 1

                aURL = preSelector.xpath('//div[@class="paginate-container"]/div/a/@href').extract()
                disabled = preSelector.xpath(
                    '//div[@class="paginate-container"]/div/span[@class="disabled"]/text()').extract_first()
                if disabled == "Next":
                    print('尾页')
                    if len(self.followingStack) > 0:
                        print("换新页")
                        maxFloowingURL = self.followingStack.pop()[0]
                        self.recordURLString += " " + maxFloowingURL
                        yield Request(maxFloowingURL, meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.gotoUser)
                    else:
                        print("停止")
                        if navSelector[3] > 0:
                            changeURL = profileURL + "?tab=following"
                            yield Request(changeURL, meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.gotoUser)
                        else:
                            print("未处理")
                elif len(aURL) > 1:
                    print('中间页')
                    if len(aURL[1]) > 0:
                        print("换新页")
                        print(aURL[1])
                        yield Request(aURL[1], meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.gotoUser)
                    else:
                        print("为空")
                        if navSelector[3] > 0:
                            changeURL = profileURL + "?tab=following"
                            yield Request(changeURL, meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.gotoUser)
                        else:
                            print("未处理")
                elif len(aURL) > 0:
                    print("首页")
                    if len(aURL[0]) > 0:
                        print("换新页")
                        print(aURL[0])
                        yield Request(aURL[0], meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.gotoUser)
                    else:
                        print("为空")
                        if navSelector[3] > 0:
                            changeURL = profileURL + "?tab=following"
                            yield Request(changeURL, meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.gotoUser)
                        else:
                            print("未处理")
                else:
                    print('不足一页')
                    if len(self.followingStack) > 0:
                        print("换新页")
                        maxFloowingURL = self.followingStack.pop()[0]
                        self.recordURLString += " " + maxFloowingURL
                        yield Request(maxFloowingURL, meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.gotoUser)
                    else:
                        print("停止")
                        if navSelector[3] > 0:
                            changeURL = profileURL + "?tab=following"
                            yield Request(changeURL, meta={'cookiejar': response.meta['cookiejar']},
                                          callback=self.gotoUser)
                        else:
                            print("未处理")
        except (TypeError, ValueError) as e:
            print("错误456")
            print(e)
        except:
            print("错误456T")

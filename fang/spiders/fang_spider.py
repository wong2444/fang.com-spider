# -*- coding: utf-8 -*-
import scrapy
import re
from fang.items import NewHouseItem, ESFHouseItem
from scrapy_redis.spiders import RedisSpider


class FangSpiderSpider(RedisSpider):
    name = 'fang_spider'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:start_urls"

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None
        for tr in trs:
            tds = tr.xpath(".//td[not(@class)]")
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get()
            province_text = re.sub(r"\s", "", province_text)
            if province_text:
                province = province_text
            if province == "其它":
                continue
            city_td = tds[1]
            city_links = city_td.xpath(".//a")
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()

                url_module = city_url.split("//")
                scheme = url_module[0]
                domain = url_module[1]
                if 'bj.' in domain:
                    newhouse_url = "https://newhouse.fang.com/house/s/"
                    esf_url = "https://esf.fang.com/"

                else:
                    domain_arr = domain.split(".")
                    # 構建新房的url鏈接
                    newhouse_url = scheme + "//" + domain_arr[0] + "." + "newhouse" + "." + domain_arr[1] + "." + \
                                   domain_arr[2] + "house/s/"
                    # 構建二手房的url鏈接
                    esf_url = scheme + "//" + domain_arr[0] + "." + "esf" + "." + domain_arr[1] + "." + domain_arr[2]

                # yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse, meta={"info": (province, city)})
                yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={"info": (province, city)})

    def parse_newhouse(self, response):
        province, city = response.meta.get('info')
        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get().strip()
            house_type_list = li.xpath(".//div[@class='house_type']/a/text()").getall()
            house_type_list = list(map(lambda x: re.sub(r"\s", "", x), house_type_list))
            rooms = list(filter(lambda x: x.endswith("居"), house_type_list))
            area = "".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())
            area = re.sub(r"\s|－|/", "", area)
            address = li.xpath(".//div[@class='address']/a/@title").get()
            district_text = "".join(li.xpath(".//div[@class='address']/a//text()").getall())
            district = re.search(r".*\[(.+)\].*", district_text).group(1)
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "", price)
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            item = NewHouseItem(name=name, rooms=rooms, area=area, address=address, district=district, sale=sale,
                                price=price, origin_url=origin_url, province=province, city=city)
            yield item
        next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse,
                                 meta={"info": (province, city)})

    def parse_esf(self, response):
        province, city = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")

        for dl in dls:
            item = {}

            infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
            infos = list(map(lambda x: re.sub(r"\s", "", x), infos))
            if infos is not None:
                name = dl.xpath(".//span[@class='tit_shop']/text()").get()
                address = dl.xpath(".//p[@class='add_shop']/span/text()").get()
                price = dl.xpath(".//dd[@class='price_right']/span[@class='red']//text()").getall()
                price = re.sub("\s", "", "".join(price))
                unit = dl.xpath(".//dd[@class='price_right']/span[last()]/text()").get()
                unit = re.sub("\s", "", unit)
                origin_url = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
                origin_url = response.url[:-2] + origin_url

                item['rooms'] = infos[0]
                item['floor'] = infos[2]
                item['area'] = infos[1]
                item['toward'] = infos[3]
                try:
                    year = infos[4]
                    item['year'] = re.sub("年建", "", year)
                except:
                    item['year'] = ''

                item['address'] = address
                item['price'] = price
                try:
                    item['unit'] = unit

                except:
                    item['unit'] = ''
                item['unit'] = unit
                item['origin_url'] = origin_url
                item['province'] = province
                item['city'] = city
                item['name'] = name
                item = ESFHouseItem(**item)
                yield item
                next_url = response.xpath("//div[@class='page_al']/p/a/@href").get()
                next_url = response.url[:-2] + next_url
                if next_url:
                    yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf,
                                         meta={"info": (province, city)})

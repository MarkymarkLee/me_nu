from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as Soup
import os
import time

# chromedriver info
chrome_driver_path = 'path/to/chromedriver'
chrome_options = Options()
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://www.google.com/maps/place/Second+Floor+%E8%B2%B3%E6%A8%93%E5%B8%AB%E5%A4%A7%E5%BA%97/@25.084762,121.4058363,12z/data=!4m12!1m2!2m1!1z5LqM5qiT!3m8!1s0x3442a985824a024f:0xdb361cbf6534e879!8m2!3d25.025405!4d121.5282001!9m1!1b1!15sCgbkuozmqJNaCSIH5LqMIOaok5IBE2FtZXJpY2FuX3Jlc3RhdXJhbnTgAQA!16s%2Fg%2F11c1slbn66?authuser=0&entry=ttu")


# 滾動頁面
def scroll_section(number):
    for _ in range(number):
        sections = driver.find_elements(
            By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')
        if len(sections) >= 3:
            section = sections[2]  # Get the third section (index 2)
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", section)
            time.sleep(1)  # Adjust the wait time as needed
        else:
            print(
                "The section with the specified classes was not found or there are less than such sections.")


# Function to click on "顯示更多" buttons
def click_show_more_buttons():
    more_buttons = driver.find_elements(
        By.XPATH, '//button[contains(@class, "w8nwRe kyuRq") and contains(@aria-label, "顯示更多")]')
    for button in more_buttons:
        button.click()
        # time.sleep(1)  # Adjust the wait time as needed


# Helper function to check if the review is within 4 years
def is_within_years(year, date_string):
    if " 年前" in date_string:
        years_ago = int(date_string.split(" ")[0])
        return years_ago <= year
    return True


# 爬review
def google_review(scroll_iterations, year_ago):
    time.sleep(3)
    scroll_section(scroll_iterations)
    time.sleep(3)
    click_show_more_buttons()
    time.sleep(3)
    # Get page source after scrolling and clicking
    page_source = driver.page_source
    # Close the browser
    driver.quit()

    # Parse page source with BeautifulSoup
    soup = Soup(page_source, "html.parser")
    # Find all review elements
    all_reviews = soup.find_all('div', class_='jftiEf')

    # Initialize a string to collect the reviews
    all_reviews_text = ""
    review_count = 0

    with open("output_reviews_0705.txt", "w", encoding="utf-8") as file:
        for review in all_reviews:
            reviewer_name = review.find('div', class_='d4r55').text.strip()
            subtitle_review = review.find('div', class_='RfnDt').text.strip()

            star_element = review.find('span', class_='kvMYJc')
            if star_element:
                star_review = star_element.get('aria-label').strip()
            else:
                star_review = 'No rating'

            date_element = review.find('span', class_='rsqaWe')
            if date_element:
                date_review = date_element.text.strip()
            else:
                date_review = 'No date'

            text_review_element = review.find('span', class_='wiI7pd')
            if text_review_element:
                text_review = text_review_element.text.strip()
            else:
                text_review = 'No text'

            # Filter out reviews older than 4 years and write to file if valid
            if text_review != 'No text' and is_within_years(year_ago, date_review):
                review_count += 1
                file.write("Reviewer: {}\n".format(reviewer_name))
                file.write("Subtitle: {}\n".format(subtitle_review))
                file.write("Rating: {}\n".format(star_review))
                file.write("Date: {}\n".format(date_review))
                file.write("Review: {}\n".format(text_review))
                file.write("\n")

                # Append the text review to the string
                all_reviews_text += f"{review_count}. {text_review}\n\n"

    # Print or use the resulting string as needed
    # print(all_reviews_text)
    print("output_reviews_0705.txt done")
    print("Total get ", review_count, " review.")
    return all_reviews_text


# llm
def gen_recommendation(personal_info, personal_prefer, menu_info, review_info, today_request):
    # 設定對話模型
    openai_api_key = os.getenv("OPENAI_API_KEY")
    chat = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.2,
        openai_api_key=openai_api_key
    )

    # 進行對話
    messages = [
        SystemMessage(
            content="綜合考量用戶個人飲食偏好、用戶個人推薦方式偏好、餐廳菜單、google maps評論，幫助用戶決定要吃什麼。用台式俗氣白話文，可以的話加表情符號。"),
        HumanMessage(
            content=f"我的飲食偏好：{personal_info}。推薦方式偏好：{personal_prefer}。菜單：{menu_info}。google maps 評論：{review_info}。我今天的要求是{today_request}，你能從菜單中選一個並告訴我為什麼嗎？"),
    ]

    response = chat(messages)
    return response


# review setting
scroll_iterations = 5   # 滾動幾次
year_ago = 4    # 讀取到幾年前的評價


# 測試函數
personal_info = "喜歡的： 清爽口感的食物,  味道較重的食物, 甜飲,  乳酸菌相關飲品, 烤肉, 印度菜,  巧克力, 墨西哥菜,  肉類,  高蛋白質食物,  複合口味飲品,  米糕, 巧克力布朗尼, 泰國菜, 芋頭, 義大利麵, 炸雞,  甜食,  濃郁口味的食品, 牛肉, 香菜, 美式咖啡,  份量多的食物,  簡單原味的食材,  高咖啡因的飲品,  蛋,  中式早餐, 鐵板麵,  馬鈴薯泥,  綠茶, 烤魚,  風味濃郁的食物,  油炸食物,  台式早餐,  碳水化合物豐富的食物,  豪華或豐盛的餐點,  熱食,  西餐, 天婦羅"
personal_prefer = "依照推薦程度排序3個餐點給我。每個餐點100字的推薦內容。在最後排序推薦的餐點名稱。"
menu_info = "Name: 貳樓金牌鹽水雞沙拉, Description: (微辣) 綜合生菜、雞肉、山苦瓜、小蕃茄、季節時蔬、青蔥、辣椒粉、鹹水雞油醋, Original Price: NT$350, Special Price: NT$280.  Name: 低碳-舒肥雞藜麥花椰飯, Description: 綜合生菜、花椰菜米、奶油炒菇、起司嫩蛋、藜麥小米、起司絲、胡麻醬(含堅果)、舒肥雞, Original Price: NT$400, Special Price: NT$320.  Name: 實打實招牌漢堡, Description: 漢堡肉為七分熟，食用時請小心碎軟骨！牛肉餅、黃起司、培根、炸魚條、巴薩米克醋膏、翹翹薯, Original Price: NT$450, Special Price: NT$360.  Name: 水牛城辣雞翅, Description: (極辣) 美式酸辣雞翅、辣海地醃菜、烤檸檬, Original Price: NT$330, Special Price: NT$264.  Name: 墨西哥雞肉酥餅, Description: Salsa醬(微辣)、酪梨醬、起司、洋蔥、BBQ醬、雞肉墨西哥酥餅, Original Price: NT$300, Special Price: NT$240.  Name: 酥炸鮮魷佐雞尾酒醬, Description: 魷魚、辣雞尾酒醬、薯類、烤檸檬, Original Price: NT$290, Special Price: NT$232.  Name: 墨西哥德腸酥餅, Description: Salsa醬(微辣)、酪梨醬、起司、洋蔥、BBQ醬、德腸墨西哥酥餅, Original Price: NT$300, Special Price: NT$240.  Name: 舊金山蒜香薯條, Description: 薯條、香蒜橄欖油, Original Price: NT$210, Special Price: NT$168.  Name: 松露薯條, Description: 薯條、松露醬、起司絲, Original Price: NT$250, Special Price: NT$200.  Name: 經典凱薩沙拉, Description: 綜合生菜、Salsa 醬(微辣) 、蒜味麵包、小蕃茄、黑橄欖、季節時蔬、起司絲、凱薩醬(含海鮮成份), Original Price: NT$320, Special Price: NT$256.  Name: 經典燻鮭魚凱薩沙拉, Description: 綜合生菜、Salsa 醬(微辣) 、蒜味麵包、小蕃茄、黑橄欖、季節時蔬、起司絲、凱薩醬(含海鮮)、燻鮭魚、溏心蛋, Original Price: NT$400, Special Price: NT$320.  Name: 經典舒肥雞凱薩沙拉, Description: 綜合生菜、Salsa 醬(微辣) 、蒜味麵包、小蕃茄、黑橄欖、季節時蔬、起司絲、凱薩醬(含海鮮)、舒肥雞, Original Price: NT$380, Special Price: NT$304.  Name: 貳樓金牌鹽水雞沙拉, Description: (微辣) 綜合生菜、雞肉、山苦瓜、小蕃茄、季節時蔬、青蔥、辣椒粉、鹹水雞油醋, Original Price: NT$350, Special Price: NT$280.  Name: 低碳-舒肥雞藜麥花椰飯, Description: 綜合生菜、花椰菜米、奶油炒菇、起司嫩蛋、藜麥小米、起司絲、胡麻醬(含堅果)、舒肥雞, Original Price: NT$400, Special Price: NT$320.  Name: 低碳-香煎魚排藜麥花椰飯, Description: 綜合生菜、花椰菜米、奶油炒菇、起司嫩蛋、藜麥小米、起司絲、胡麻醬(含堅果)、巴沙魚, Original Price: NT$370, Special Price: NT$296.  Name: 實打實招牌漢堡, Description: 漢堡肉為七分熟，食用時請小心碎軟骨！牛肉餅、黃起司、培根、炸魚條、巴薩米克醋膏、翹翹薯, Original Price: NT$450, Special Price: NT$360.  Name: 老墨辣鞭炮漢堡, Description: 漢堡肉為七分熟，食用時請小心碎軟骨！(微辣) 牛肉餅、黃起司、炸墨西哥辣椒、BBQ醬、翹翹薯, Original Price: NT$390, Special Price: NT$312.  Name: 低碳-碳烤牛排藜麥花椰飯, Description: 舒肥牛排為固定熟度喔！綜合生菜、花椰菜米、藜麥小米、奶油炒菇、起司嫩蛋、起司絲、胡麻醬(含堅果)、舒肥牛肉, Original Price: NT$570, Special Price: NT$456.  Name: 生酮總匯海陸拼盤, Description: 舒肥牛排為固定熟度喔！綜合生菜、奶油炒菇、起司嫩蛋、起司絲、紅葡萄酒醋、舒肥牛肉、巴沙魚, Original Price: NT$570, Special Price: NT$456.  Name: 厚烤奶油 Ham 三明治, Description: 歐式麵包、經典火腿、黃起司、半熟太陽蛋(微辣)、辣海地醃菜、翹翹薯, Original Price: NT$360, Special Price: NT$288.  Name: 橙香法式丹麥 Sunny 舒肥雞, Description: 橙香丹麥、舒肥雞、生菜、藜麥小米、半熟太陽雙蛋(微辣)、薯類、焦糖漿, Original Price: NT$460, Special Price: NT$368.  Name: 經典牛肉奶油炒菇班尼蛋, Description: 歐式麵包、綜合生菜、燻牛肉、奶油炒菇、水波蛋、起司醬、巴薩米克醋膏膏、翹翹薯, Original Price: NT$460, Special Price: NT$368.  Name: 橙香法式丹麥佐水波海鮮洋芋, Description: 橙香丹麥、海鮮洋芋、生菜、藜麥小米、洋蔥、奶油炒菇、水波蛋、起司醬、巴薩米克醋膏、焦糖漿, Original Price: NT$460, Special Price: NT$368.  Name: 燻鮭魚奶油炒菇班尼蛋, Description: 歐式麵包、燻鮭魚、酸豆、綜合生菜、奶油炒菇、水波蛋、起司醬、巴薩米克醋膏、翹翹薯, Original Price: NT$470, Special Price: NT$376.  Name: 橙香法式丹麥舒肥牛排, Description: 舒肥牛排為固定熟度喔！橙香丹麥、舒肥牛肉、半熟太陽蛋(微辣)、綜合生菜、翹翹薯、胡麻醬(含堅果)、焦糖漿、炸蒜碎, Original Price: NT$590, Special Price: NT$472.  Name: 橙香法式丹麥 MINI, Description: 橙香丹麥、綜合生菜、培根、太陽蛋、薯類、胡麻醬(含堅果)、焦糖漿, Original Price: NT$360, Special Price: NT$288.  Name: 經典火腿班尼蛋, Description: 歐式麵包、綜合生菜、經典火腿、奶油炒菇、水波蛋、起司醬、巴薩米克醋膏、翹翹薯, Original Price: NT$380, Special Price: NT$304.  Name: 總匯芝心歐姆蕾, Description: 歐姆蛋、辣Pico de Gallo 蒜麵包、奶油炒菇、玉米、蕃茄、火腿、德腸、辣海地醃菜、雙色起司、翹翹薯, Original Price: NT$390, Special Price: NT$312.  Name: 烏斯特肉醬歐姆蕾, Description: 歐姆蛋、辣Pico de Gallo 蒜麵包、烏斯特肉醬(含牛、豬、海鮮)、辣海地醃菜、雙色起司、翹翹薯, Original Price: NT$400, Special Price: NT$320.  Name: 橙香法式丹麥蕈菇水波洋芋, Description: 橙香丹麥、生菜、蕈菇洋芋、洋蔥、藜麥小米、水波蛋、起司醬、巴薩米克醋、焦糖漿, Original Price: NT$390, Special Price: NT$312.  Name: 酒香蒜味蛤蜊墨魚麵, Description: (孕婦不宜) 「重口味愛好者很是喜歡」酒、蒜、奶油、九層塔、蛤蜊, Original Price: NT$370, Special Price: NT$296.  Name: 南洋辛香雙料細扁麵, Description: (小辣 / 堅果) 南洋醬、雞肉、蝦子、季節時蔬, Original Price: NT$370, Special Price: NT$296.  Name: 經典青醬鮮蝦細扁麵, Description: (海鮮 / 堅果) 青醬、蝦子、季節時蔬、炸蒜片、起司絲, Original Price: NT$390, Special Price: NT$312.  Name: 香爆椒麻唐揚雞細扁麵, Description: (極辣) 茄汁、雞塊、朝天乾辣椒、九層塔、起司絲, Original Price: NT$380, Special Price: NT$304.  Name: 越式酸辣海賊細扁麵, Description: (小辣) 洋蔥、魷魚、小蕃茄、九層塔、香菜, Original Price: NT$370, Special Price: NT$296.  Name: 曙光汁鮮蝦雞肉細扁麵, Description: 曙光奶油醬、雞肉、蝦子、起司絲、季節時蔬, Original Price: NT$390, Special Price: NT$312.  Name: 家鄉肉醬麵佐老媽子的肉丸, Description: 烏斯特茄汁肉醬(含牛、豬、海鮮)、牛肉丸、九層塔、起司絲, Original Price: NT$410, Special Price: NT$328.  Name: 台式熱炒鹹蛋苦瓜麵, Description: (微辣) 鹹香白醬、培根、山苦瓜、洋蔥、炸杏鮑菇, Original Price: NT$360, Special Price: NT$288.  Name: 馬德里臘腸海鮮飯, Description: (小辣 / 孕婦不宜) 酒、蝦子、德腸、蛤蠣、季節時蔬、薑黃飯、起司絲, Original Price: NT$390, Special Price: NT$312.  Name: 藍帶豬排奶油焗烤飯, Description: (孕婦不宜) 曙光奶油醬、藍帶豬排、培根、季節時蔬、起司、薑黃飯, Original Price: NT$420, Special Price: NT$336.  Name: 漢堡排+飯+黑胡椒醬=讚, Description: (小辣 / 孕婦不宜)漢堡肉為七分熟，食用時請小心碎軟骨！牛肉餅、黑胡椒醬、杏鮑菇、半熟太陽蛋、藜麥小米、生菜、起司、薑黃飯, Original Price: NT$390, Special Price: NT$312.  Name: 巴薩米克蕈菇細扁麵, Description: 特製雙醋醬、綜合菇、生菜、藜麥小米、 半熟太陽蛋, Original Price: NT$360, Special Price: NT$288.  Name: 松露蕈菇奶油細扁麵, Description: 松露奶油醬、綜合菇、巧克力、起司絲, Original Price: NT$390, Special Price: NT$312.  Name: BBQ溫烤半鷄, Description: 香嫩半鷄、BBQ 醬、炒季節時蔬、薯條, Original Price: NT$720, Special Price: NT$576.  Name: 主廚脆皮豬腳, Description: 脆皮豬腳、德式酸菜、黃芥末、炒季節時蔬、薯條, Original Price: NT$760, Special Price: NT$608.  Name: 吃光光雞肉蛋包飯, Description: (孕婦不宜) 曙光奶油醬、雞塊、蛋皮、季節時蔬、薑黃飯、多多蜜桃凍(含動物性膠質), Original Price: NT$290, Special Price: NT$232.  Name: 熊孩子的奶油雞肉麵, Description: (海鮮) 白醬、雞塊、起司、季節時蔬、起司絲、多多蜜桃凍(含動物性膠質), Original Price: NT$290, Special Price: NT$232.  Name: 大俠愛吃漢寶寶, Description: 牛肉、雞塊、起司、生菜、薯條、 美奶滋、多多蜜桃凍(含動物性膠質), Original Price: NT$280, Special Price: NT$224.  Name: 天堂鳥冰茶, Description: 蛋奶素者不可食用 !!天堂鳥茶、水蜜桃凍、綠檸檬, Original Price: NT$160, Special Price: NT$128.  Name: 熱-女巫 Sangria(無酒精), Description: 天堂鳥茶、肉桂、柳橙、藍莓、迷迭香、 接骨木、葡萄, Original Price: NT$150, Special Price: NT$120.  Name: 桃花朵朵開運茶(脫單靠這杯), Description: 鹽味奶油、檸檬茶、水蜜桃果泥、接骨木花(奶霜於外帶過程中可能與飲品融合哦）, Original Price: NT$150, Special Price: NT$120.  Name: 粉紅芭樂蘋果汁, Description: 蔬果汁皆為去冰喔 !!芭樂、蘋果、甜菜根、甘蔗汁、明日葉, Original Price: NT$200, Special Price: NT$160.  Name: 橙橘胡蘿蔔芭樂汁, Description: 蔬果汁皆為去冰喔 !!胡蘿蔔、芭樂、甘蔗汁、明日葉, Original Price: NT$200, Special Price: NT$160.  Name: 洋紅甜菜葡萄汁, Description: 蔬果汁皆為去冰喔 !!甜菜根、葡萄、芭樂、甘蔗汁、明日葉, Original Price: NT$200, Special Price: NT$160.  Name: 羽衣甘藍果汁, Description: 蔬果汁皆為去冰喔 !!羽衣甘藍、蘋果、明日葉, Original Price: NT$200, Special Price: NT$160.  Name: 冰-經典拿鐵, Description: 綠檸檬、雪碧、咖啡, Original Price: NT$150, Special Price: NT$120.  Name: 熱-經典拿鐵, Description: 鹽味奶油、啤酒花、牛奶、咖啡(奶霜於外送過程中可能與飲品融合哦）, Original Price: NT$150, Special Price: NT$120.  Name: 冰-美式咖啡, Description: (4吋) 貳樓招牌巧克力蛋糕與香濃起司餡, Original Price: NT$130, Special Price: NT$104.  Name: 熱-美式咖啡, Description: (4吋) 起司蛋糕、Oreo碎, Original Price: NT$130, Special Price: NT$104.  "
review_info = google_review(scroll_iterations, year_ago)
today_request = "不超過500元的食物"


print(gen_recommendation(personal_info, personal_prefer,
      menu_info, review_info, today_request))

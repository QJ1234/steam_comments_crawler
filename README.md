
# steam_comments_crawler

这是一个爬取steam上某个游戏评论数据的脚本
This is a script designed to scrape review data for a specific game on Steam.

这个仓库参考了[Chaobs](https://github.com/Chaobs/Steam-Comments-Collector)以及[Muxiner](https://github.com/Muxiner/Steam-Comments-Collector)，参考了博客[ https://cloud.tencent.com/developer/article/1085988 ](https://cloud.tencent.com/developer/article/1085988)

在他们的基础上进行了改进，去掉了一些处理以适应更多语言，并且加入了断点续传，使得连续爬取大量评论成为可能。


This repository draws inspiration from [Chaobs](https://github.com/Chaobs/Steam-Comments-Collector) and [Muxiner](https://github.com/Muxiner/Steam-Comments-Collector), as well as the blog post [https://cloud.tencent.com/developer/article/1085988](https://cloud.tencent.com/developer/article/1085988).

Building upon their work, improvements have been made to adapt the script for a wider range of languages by removing certain processing steps. 

Additionally, a checkpoint recovery feature has been implemented, enabling the continuous scraping of large volumes of reviews.

# Install 

clone我的仓库，然后安装依赖项

```
pip install -r requeirements.txt
```

use git clone my repo,then install requeirements

# How to use

首先进入你想要爬取评论的游戏的商店界面，随后滑到最底下，点击浏览所有评测。然后显示栏选择最新，要爬好评还是差评还是都爬你自己决定，右边的语言选择你自己的语言。**注意：尽量保证你的界面语言和你选择的评论语言是一致的。**

然后打开repo里的configs.json，将这个网页的网址复制到url后，例如：

https://steamcommunity.com/app/2527500/reviews/?p=1&browsefilter=mostrecent&filterLanguage=schinese   ~~都给我去玩米塔！！！~~

你可以看到configs中除了url，还有几个参数

#### game_id：

你会发现网址中会有一串数字，在例子中就是：

https://steamcommunity.com/app/**2527500**/reviews/?p=1&browsefilter=mostrecent&filterLanguage=schinese

将数字复制出来，填在game_id之后

#### num_comments:

你想要爬取的评论数量，填数字

#### language:

在你的网志中可以发现你的语言：

https://steamcommunity.com/app/2527500/reviews/?p=1&browsefilter=mostrecent&filterLanguage=**schinese**

将其复制到language后，注意是字符串。

#### file_name:

你想要保存的文件名称，**需要以.csv结尾**

#### headers:

这个参数你只需要修改后面的Accept-Language后的内容，你需要在你刚才打开的浏览器的页面中按下F12，在headers中找到Accept-Language，将后面的内容复制到字符串中。


### 参数填好之后就可以运行

```
python crawler.py
```



First, navigate to the store page of the game for which you wish to scrape reviews. Scroll to the bottom and click on "View all reviews." Then, select "Most recent" from the display options, and decide whether you want to scrape positive, negative, or all reviews. On the right side, choose your preferred language. **Note: Ensure that your interface language matches the language of the reviews you have selected.**

Next, open the `configs.json` file in the repository and copy the URL of this webpage into the `url` field, for example:

https://steamcommunity.com/app/2527500/reviews/?p=1&browsefilter=mostrecent&filterLanguage=schinese   ~~Go play Miside!!!~~

You will notice that in addition to `url`, there are several other parameters in `configs`.

#### game_id:

You will see a string of numbers in the URL, in the example it is:

https://steamcommunity.com/app/**2527500**/reviews/?p=1&browsefilter=mostrecent&filterLanguage=schinese

Copy this number and paste it after `game_id`.

#### num_comments:

The number of reviews you wish to scrape, enter a number.

#### language:

You can identify your language in the URL:

https://steamcommunity.com/app/2527500/reviews/?p=1&browsefilter=mostrecent&filterLanguage=**schinese**

Copy this to the `language` field, note that it should be a string.

#### file_name:

The name of the file you wish to save, **it must end with `.csv`**.

#### headers:

For this parameter, you only need to modify the content after `Accept-Language`. You need to press F12 on the page you just opened in your browser, find `Accept-Language` in the headers, and copy the content after it into the string.


### Once the parameters are filled in, you can proceed to run the script:

```
python crawler.py
```

# Note

##### 文件中最后一列的user_reviews_cursor是用于断点续传的，当你的爬虫结束之后，你就可以删除这一列。

##### 在爬虫之前请在商店中确认你的语言中的总评论数量

能爬到的评论数不会超过商店中显示的评论数，一旦超出总量，会报错Nonetype，停止运行即可

##### 文件中的各项数据都没有经过很精细的处理，因为每种语言不同处理逻辑无法通用，因此需要你在爬虫结束后根据自己的数据自己处理

##### steam会有反爬机制，因此我设置了request的timeout为5s，如果你的网速很快可以改低3s甚至1s


**The `user_reviews_cursor` in the last column of the file is used for checkpoint recovery. You can delete this column after your crawler has finished running.**

Before running the crawler, please confirm the total number of reviews in your selected language on the store page.The number of reviews that can be scraped will not exceed the total number displayed in the store. If the scraper attempts to go beyond this limit, it will throw a `Nonetype` error, and you can simply stop the process.

**The data in the file has not been finely processed**, as the processing logic cannot be universally applied across different languages. Therefore, you will need to process the data according to your specific needs after the scraping is complete.

**Steam has anti-scraping mechanisms in place**, so I have set the `request` timeout to 5 seconds. If your internet connection is fast, you can reduce this to 3 seconds or even 1 second.


# last

如果你遇到问题，请在issue中提出来，觉得有用的话欢迎给我的项目一个star。

If you encounter any issues, please raise them in the Issues section. If you find this project useful, kindly give it a star.

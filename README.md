## 豆瓣我读， 我看爬虫

Python所写，爬取豆瓣[我读](https://book.douban.com/mine)， 豆瓣[我看](https://movie.douban.com/mine)的爬虫，方便大家保存自己的收藏！


### 使用说明

登录自己的豆瓣账号，然后把源文件里的 `cookies`里的`gr_user_id` 替换成自己的， 然后运行以下命令行。
  - `python douban.py book --user-id USER_ID`
  - `python douban.py movie --user-id USER_ID`

程序输出JSON格式的信息。
`USER_ID` 为你自己的豆瓣的USER ID.


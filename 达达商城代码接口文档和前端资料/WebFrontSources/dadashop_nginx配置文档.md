[toc]

## DADASHOP  测试配置文档  Ubuntu18.04

**以下文档以python教学环境为准**

### 1.  安装nginx

```shell
# 安装nginx
tarena@aid:~$ sudo apt-get install nginx

# 查看nginx启动状况
tarena@aid:~$ sudo service nginx status

# 启动/重启/停止等服务  两种方式如下
tarena@aid:~$ sudo service nginx [start|restart|stop]
tarena@aid:~$ sudo sudo /etc/init.d/nginx [start|restart|stop]
```

<font color=red>ubuntu版本中的nginx HTML 页面的路径为 　**/var/www/html**</font>



### 2. nginx 配置 - 前端页面

1. 创建dadashop项目配置文件

   sudo vim /etc/nginx/conf.d/dadashop.conf

   <font color=red>注意：每次修改配置文件后要重启nginx服务</font>

   ```nginx
   server {
           
           listen 7000 default_server;
           listen [::]:7000 default_server;
           server_name __;
   
           root /var/www/html;
           # Add index.php to the list if you are using PHP
           index index.html index.htm index.nginx-debian.html;
   
           location / {
                   # First attempt to serve request as file, then
                   # as directory, then fall back to displaying a 404.
                   try_files $uri $uri/ =404;
           }
   }
   ```

2. <font color=red>配置完毕后可在终端中 直接输入 nginx -t   查看配置文件是否有语法错误</font>

   ```python
   tarena@tedu:~$ sudo nginx -t
       
   nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
   nginx: configuration file /etc/nginx/nginx.conf test is successful
   #此例为配置文件 检查通过
   ```

3. 重新启动nginx服务

   ```python
   # 方式一：平滑重启nginx【访问用户无感知】
   	sudo nginx -s reload 
       
   # 方式二：直接重启nginx
   	sudo /etc/init.d/nginx restart
   ```



### 3. 创建存放html目录及拷贝文件 

1. 创建 /var/www/html/dadashop/ 目录

   ```shell
   tarena@tedu:~$ sudo mkdir /var/www/html/dadashop/
   ```

2. 将client目录下的static和templates目录放到/var/www/html/dadashop目录下

   ```shell
   #假设client文件夹已在ubuntu主目录下，则执行如下命令即可
   sudo cp -fr client/.  /var/www/html/dadashop/
   ```



### 4. 验证

浏览器输入 http://127.0.0.1:7000/dadashop/templates/index.html  即可




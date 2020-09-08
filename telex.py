#!/usr/bin/python3
import datetime
from datetime import timedelta
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
import re
plot = """
set title "Telex támogatók száma - VALUE - TIMESTAMP"
set xtics nomirror rotate by -45
set grid ytics 500
#set grid ytics
set grid xtics
set border 1
set bmargin 4
set style fill solid 1.00 border lt -1
set style data histograms
set xtics border scale 1,0 nomirror autojustify norangelimit
set key off auto columnheader
set yrange [0:*]
set yrange [20000:28000]
set linetype 1 lc rgb '#183693'
set terminal png font "/usr/share/fonts/truetype/freefont/FreeSans.ttf" \
12 size 1024,768
set output "counter.png"
set xdata time
set datafile separator ","
set timefmt '%Y/%m/%d %H:%M'
set xrange ["2020/09/06 18:00":"XRANGE"]
plot "counter.txt" using 1:2 with lines lw 3
"""


file_object = open('counter.txt', 'a')
tz = timezone('Europe/Budapest')
time_stamp = datetime.datetime.now(tz).strftime("%Y/%m/%d %H:%M")
x_range = datetime.datetime.now(tz)+timedelta(hours=12)
plot = re.sub(r"XRANGE", "%s" % x_range.strftime("%Y/%m/%d %H:%M"), plot)
plot = re.sub(r"TIMESTAMP", "%s" % time_stamp, plot)

url = 'https://tamogatas.telex.hu/'
chrome_driver_path = '/home/balogh/chromedriver'
chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
  executable_path=chrome_driver_path, options=chrome_options
)

with webdriver as driver:
    wait = WebDriverWait(driver, 1)
    driver.get(url)
    results = driver.find_elements_by_tag_name('strong')
    for the_text in results:
        if the_text.text.isnumeric():
            file_object.write('%s,%s\n' % (time_stamp, the_text.text))
            plot = re.sub(r"VALUE", "%s" % the_text.text, plot)

    driver.close()
file_object.close()
gnuplot_process = subprocess.Popen(["gnuplot"],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
gnuplot_process.stdin.write(plot.encode())
stdout_value, stderr_value = gnuplot_process.communicate()

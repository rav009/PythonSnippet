# PythonSnippet
## A python script to download blogs from CSDN and transfer the blogs to markdown format.
Fork from:
https://github.com/kesalin/PythonSnippet/blob/master/ExportCSDNBlog.py

This branch can adapt the 2018 new UI of CSDN.

Preparation：
`pip install bs4`
`pip install html5lib`

Execution:

`python ExportCSDNBlog.py`


Notices:

In the web page of CSDN, there is such a piece of code:
```
<div style="display:none;">
	<img onerror='setTimeout(function(){if(!/(csdn.net|iteye.com|baiducontent.com|googleusercontent.com|360webcache.com|sogoucdn.com|bingj.com|baidu.com)$/.test(window.location.hostname)){"\x68\x74\x74\x70\x73\x3a\x2f\x2f\x77\x77\x77\x2e\x63\x73\x64\x6e\x2e\x6e\x65\x74"}},3000);' src=""/>
</div>
```

This piece of code will make the web page redirect to the front page of CSDN if you open the web page from local file.So I added an action  in the script to remove this piece of code.

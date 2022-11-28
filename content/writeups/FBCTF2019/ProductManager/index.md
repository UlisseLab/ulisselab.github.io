---
title: Product Manager
tags:
  - web
---

## Challenge

### Inforomation

- category: web
- points: 100

### Description

> Come play with our products manager application!

> http://challenges.fbctf.com:8087

> Written by Vampire

> (This problem does not require any brute force or scanning. We will ban your team if we detect brute force or scanning).

> The flag was a column of db raw

> CREATE TABLE products (
> secret char(64),
> description varchar(250)
> );

> INSERT INTO products VALUES('facebook', sha256(....), 'FLAG_HERE');

## Writeup

### Author

### Solution

On the web page we were allowed to enter a value in the database as long as it was not an existing value.

The application php source was given and from the db.php file get_product function we find the solution to the challenge.

Loading a "facebook " product (with an additional space) the value is entered and by calling with "facebook" (without space) the fetch of the view.php takes the first value corresponding to facebook, obtaining the flag.

Resolved after trying an injection for a good hour! :(

function get_product($name) {
global $db;
$statement = $db->prepare(
"SELECT name, description FROM products WHERE name = ?"
);

```
Facebook, Inc. is an American online social media and social networking service company based in Menlo Park, California. Very cool! Here is a flag for you: fb{4774ck1n9_5q1_w17h0u7_1nj3c710n_15_4m421n9_:)}
```

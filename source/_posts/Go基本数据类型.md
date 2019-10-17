---
title: Go基本数据类型
date: 2019-07-10 10:34:26
tags: Golang
categories: 
	- Golang
---

# 基本数据类型

除了基本的整型、浮点型、布尔型、字符串外，还有数组、切片、结构体、函数、map、通道（channel）等。Go 语言的基本类型和其他语言大同小异。

<!--more-->

## 整型

整型分为无符号和有符号两个大类:

- 有符号

  > 按长度分为：int8、int16、int32、int64

- 无符号

  > uint8、uint16、uint32、uint64

其中，`uint8`就是我们熟知的`byte`型，`int16`对应C语言中的`short`型，`int64`对应C语言中的`long`型。

| 类型   | 描述                                                         |
| ------ | ------------------------------------------------------------ |
| uint8  | 无符号 8位整型 (0 到 255)                                    |
| uint16 | 无符号 16位整型 (0 到 65535)                                 |
| uint32 | 无符号 32位整型 (0 到 4294967295)                            |
| uint64 | 无符号 64位整型 (0 到 18446744073709551615)                  |
| int8   | 有符号 8位整型 (-128 到 127)                                 |
| int16  | 有符号 16位整型 (-32768 到 32767)                            |
| int32  | 有符号 32位整型 (-2147483648 到 2147483647)                  |
| int64  | 有符号 64位整型 (-9223372036854775808 到 9223372036854775807) |

通过不同制式表示整型:

```
func fmtNum() {
    // 十进制
    var a int = 10
    fmt.Printf("%b \n", a)  // 1010

    // 八进制
    fmt.Printf("%o \n", a)  // 12

    //十六进制
    fmt.Printf("%x \n", a)  // a
    fmt.Printf("%X \n", a)  // A
}
```

 

## 浮点数

Go语言支持两种浮点型数：`float32`和`float64`。这两种浮点型数据格式遵循`IEEE 754`标准： `float32` 的浮点数的最大范围约为 `3.4e38`，可以使用常量定义：`math.MaxFloat32`。 `float64` 的浮点数的最大范围约为 `1.8e308`，可以使用一个常量定义：`math.MaxFloat64`。

```
func fmtFloat() {
    var b float32 = 3.1415

    fmt.Printf("%f \n", b)  // 3.141500 
    fmt.Printf("%.3f \n", b)  // 3.141
}
```

 

## 布尔

Go语言中以`bool`类型进行声明布尔型数据，布尔型数据只有`true`和`false`两个值。

**注意：**

- 布尔类型变量的默认值为`false`。
- Go 语言中不允许将整型强制转换为布尔型.
- 布尔型无法参与数值运算，也无法与其他类型进行转换。

## 字符串

- 多行字符串

  ```
  str := `第一行
  第二行
  第三行
  `
  ```

   

- 字符串操作

  | 方法                                                         | 介绍           |
  | ------------------------------------------------------------ | -------------- |
  | len(str)                                                     | 求长度         |
  | +或fmt.Sprintf                                               | 拼接字符串     |
  | strings.Split(str, sep)                                      | 分割           |
  | strings.contains(str, substr)                                | 判断是否包含   |
  | strings.HasPrefix(str, prefix),strings.HasSuffix(str, suffix) | 前缀/后缀判断  |
  | strings.Index(str, substr),strings.LastIndex(str, substr)    | 子串出现的位置 |
  | strings.Join(a[]string, sep string)                          | join操作       |

  `e.g`

  ```
  func strOperator() {
      str := "goingtu"
      fmt.Println(len(str))  // 7
      fmt.Println(strings.Split(str, "g"))  // [ oin tu]
      fmt.Println(strings.Contains(str, "tu"))  // true
      fmt.Println(strings.HasPrefix(str, "go"))  // true
      fmt.Println(strings.HasSuffix(str, "tu"))  // true
      fmt.Println(strings.Index(str, "g"))  // 0
      fmt.Println(strings.LastIndex(str, "g"))  // 4
  
      b := []string{"1", "2", "3"}
      fmt.Println(strings.Join(b, ","))  // "1,2,3"
  }
  ```

   

   

## byte和rune类型

组成每个字符串的元素叫做“字符”，可以通过遍历或者单个获取字符串元素获得字符。

Go 语言的字符有以下两种：

1. `uint8`类型，或者叫 byte 型，代表了`ASCII码`的一个字符。
2. `rune`类型，代表一个 `UTF-8字符`。

当需要处理中文、日文或者其他复合字符时，则需要用到`rune`类型。`rune`类型实际是一个`int32`。

```
func loopStr()  {
    a := "hello 大家好！"
    for i := 0; i < len(a); i ++ { // byte
        fmt.Printf("%c", a[i])
    }
    fmt.Println()
    for _, j := range a{  // rune
        fmt.Printf("%c", j)
    }
}

// hello å¤§å®¶å¥½ï¼
// hello 大家好！
```

 

因为UTF8编码下一个中文汉字由3~4个字节组成，所以我们不能简单的按照字节去遍历一个包含中文的字符串，否则就会出现上面输出中第一行的结果。

字符串底层是一个byte数组，所以可以和`[]byte`类型相互转换。字符串是不能修改的 字符串是由byte字节组成，所以字符串的长度是byte字节的长度。 rune类型用来表示utf8字符，一个rune字符由一个或多个byte组成。

## 类型转换

```
func countZh() {
    a := "hello 大家好 ！"
    b := []rune(a)
    fmt.Println(len(b))
}
// 通过类型转换计划字符串的中文字数
```

 
---
title: Vue
date: 2019-01-01 21:34:47
tags: Vue
categories: Vue
---

# 前端有三大框架：

​			

- Vue     

- angular

- React​		

vue的思想 => 数据驱动视图

<!--more-->

# vue使用

## 指令系统

```vue
v-text 
v-html 
v-if
v-show
v-for
v-bind
v-on
```

### v-if和v-show

> `v-if `是“真正”的条件渲染，因为它会确保在切换过程中条件块内的事件监听器和子组件适当地被销毁和重建。`v-if `也是惰性的：如果在初始渲染时条件为假，则什么也不做——直到条件第一次变为真时，才会开始渲染条件块。
>
> `v-show `就简单得多——不管初始条件是什么，元素总是会被渲染，并且只是简单地基于 CSS `(display)`进行切换。

### v-on v-bind v-for

> vue中使用`v-on:click`对当前DOM绑定click事件 注意:所有的原生js的事件使用`v-on`都可以绑定
> `v-if`和`v-on `来对页面中DOM进行操作
> v-bind:class和v-on对页面中DOM的样式切换
> v-bind和v-on
> 在vue中它可以简写: v-bind:         
> :class 等价于 v-bind:class   
> :src 等价于v-bind:src
> :id 等价于v-bind:id
> v-on:click   等价于 @click = '方法名'

### v-text  v-html

> 对页面的dom进行赋值运算   相当与js中innerText innerHTML

## 组件使用

### 局部组件

- 声子 

- 挂子 

- 用子

    ```vue
    //声子
    var App = {
     tempalte:`
       <div class='app'></div>`
    };
    
    //如果实例化vue对象中既有el,又有template，如果template中定义模板的内容
    //那么template模板的优先级大于el
    new Vue({
     el:"#app",
     //用子  
     template:<App />
     //挂子
     components:{
        App
     }
    
    })
    ```


- Prop父组件向子组件传递数据

- 子组件传递数据到父组件

### 全局组件
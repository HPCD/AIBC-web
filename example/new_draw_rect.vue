<template>
  <div class="container">
    <!-- Swiper -->
    <div class="swiper-container gallery-top"></div>
    <!-- <div style="display:flex; ">
      
    </div>-->
    <canvas id="canvas" ref="canvas" width="500" height="500">这是浏览器不支持canvas时展示的信息</canvas>
    <div id="contextmenu-output"></div>
    <img id="img" src="../../images/avator.jpg" style="display: none;" />

    <!-- Add Arrows -->
    <div class="swiper-button-next swiper-button-white"></div>
    <div class="swiper-button-prev swiper-button-white"></div>
    
    <div class="swiper-container gallery-thumbs">
      <div class="swiper-wrapper">
        <div
          class="swiper-slide"
          v-for="item in banners"
          :style="'background-image:url('+item.url+');'"
          :key="item.url"
          @click="setImgCanvas(item.url)"
        ></div>
      </div>
    </div>
    <div>
      <button class="with-cool-menu">Jquery-contextmenu</button>
    </div>
    <div class="list_label">
      <ul>
        <li v-for="item in labels" :key="item">{{item}}</li>
        <el-button type="text" @click="open">
          <span style="font-size: 20px;">+</span>新增标签
        </el-button>
      </ul>
    </div>
  </div>
</template>

<script>
import vue from "vue";

import $ from "jquery";
import Swiper from "../../js/swiper-bundle.js";
import   "../../js/fabric.min.js";
import   "../../js/jquery.min.js";
import '../../js/jquery.contextMenu.min.js';
import '../../js/jquery.ui.position'
export default {
  data() {
    return {
      name: "Jquery_contextmenu_44",
      banners: [
        // {url:"http://127.0.0.1:9999/resources/images/7.jpg"}
      ],
      imgElement: {},
      canvas: null,
      firstpoint: {},
      lastPoint: {},
      contextMenuItems: null,
      position: {},
      key: "",
      object: {},
      obj_list: [],
      // currentImgUrl: "",
      imgInfos: [
        //用于存储图片信息{url:[]}
      ],
      currentUrl:null,
      imgWidthRatio: 1,//图片缩放比例默认是1
      imgHeightRatio: 1,
      singleImg: {},
      rects_list: [], //一个矩形框信息
      //lastImgInfo:[],//保存上一张图片信息
      labels: ["1", "2", "3"],
      getLabelUrl:"http://127.0.0.1:9999/src/labels",
      imgInfoUrl:"http://127.0.0.1:9999/src/img_info",
      saveLabelUrl :"http://127.0.0.1:9999/src/labels"
      //getImageUrl :"http://127.0.0.1:9999/src/labels"
    };
  },
  created() {
    //从本地中加载数据   或 从数据库中获取数据

    let _this = this;
    
    this.initLabelData();
    console.log("结束之后为 ", _this.labels);
    this.getImageUrlList()
  },
  mounted() {
    
    //  设置图片缩略图
    var galleryThumbs = new Swiper(".gallery-thumbs", {
      spaceBetween: 10,
      slidesPerView: 5,
      freeMode: true,
      watchSlidesVisibility: true,
      watchSlidesProgress: true,
    });
    var galleryTop = new Swiper(".gallery-top", {
      spaceBetween: 10,
      navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
      },
      thumbs: {
        swiper: galleryThumbs,
      },
      
      onSlideChangeEnd: function (swiperHere) {
        // alert("shezhisuoluetu")
        //获取下面的img图片
        var imgurl = $(".swiper-slide-active img").attr("src"); //当前图片url地址，上一张图片的地址
        // alert(imgurl)
        this.currentImgUrl = imgurl;
      },
    });
    //获取swiper当前显示1页url
    //初始化画板并监听画板鼠标
    this.initCanvas();
    //初始化右键菜单
    this.onloadMenu();
  },
  methods: {

    ajaxRequestFun(resUrl,resMethod,resData){
      $.ajax({
        url: resUrl,
        type: redMethod,
        data: resData,
        dataType: "json",
        success: function (data, dataTextStatus, jqxhr) {
          console.log("请求返回数据 ： ", data.data);
          resData = JSON.parse(data.data);
          return resData
        },
        error: function (jqxhr, textStatus, error) {
          console.log("__失败__");
          console.log(error);
       
        },
      });
    },
    //请求获取数据
    getImageUrlList(){
      let _this = this;
      var getImageUrl = _this.imgInfoUrl
      //后台请求数据
      $.ajax({
        url: getImageUrl,
        type: "get",
        data: { user_name: "123", device_id: "123456",dataset:"test" },
        dataType: "json",
        success: function (data, dataTextStatus, jqxhr) {
          console.log("初始化图片数据 ： ", data.data);
          _this.imgInfos = JSON.parse(data.data);
          console.log(_this.imgInfos)
          //初始化图像预览
          _this.initImageInfo()
         
        },
        error: function (jqxhr, textStatus, error) {
          console.log("__失败__");
          console.log(error);
       
        },
      });

    },
    //初始化图片信息，把图片地址加载到初始值bananers
    initImageInfo(){
      //let _this = this
      for (var i = 0; i < this.imgInfos.length; i++) {
        var imgObj = this.imgInfos[i]
        //存放img url 字典
        var imgUrlDict = {}
        imgUrlDict.url = imgObj.url
        console.log("初始化后this.imgInfos ",this.imgInfos)
       
        this.banners.push(imgUrlDict)
        
      }


    },
    // 初始化请求数据，如标签，坐标信息
    initLabelData() {
      
      // alert("d");
      let _this = this;
      // var hurl = -this.getLabelUrl;
      //后台请求数据
      $.ajax({
        url: _this.getLabelUrl,
        type: "post",
        data: { user_name: "123", device_id: "123456" },
        dataType: "json",
        success: function (data, dataTextStatus, jqxhr) {
          console.log("初始化返回标签数据 ： ", data);
          _this.labels = data.data;
        },
        error: function (jqxhr, textStatus, error) {
          console.log("__失败__");
          console.log(error);
       
        },
      });
    },

    //添加右击事件并初始化
    onloadMenu() {
     
      //需要通过_this 方能获取到contextMenuItems,否则为未识别到
      let _this = this;
      //添加右击事件
      $(".upper-canvas").contextmenu(_this.onContextmenu);
      // alert($)
      //初始化右键菜单
      $.contextMenu({
        selector: "#contextmenu-output",
        trigger: "none",
        build: function ($trigger, e) {
          
          var item = _this.contextMenuItems;
          console.log(item);
          //构建菜单项build方法在每次右键点击会执行
          return {
            callback: _this.contextMenuClick,
            items: item,
          };
        },
      });
      // alert( "ddfnfff")
    },
    //初始化画板
    initCanvas() {
      let _this = this;
      //  设置canvas
      let painting = false;
      this.firstpoint = { x: undefined, y: undefined };
      this.lastPoint = { x: undefined, y: undefined };
      this.imgElement = document.getElementById("img");
      //初始化画板
      this.canvas = new fabric.Canvas("canvas", {
        isDrawingMode: false,
        devicePixelRatio: true, // Retina 高清屏，支持
      });

      //宽高缩放比例
      this.imgWidthRatio = this.canvas.width / this.imgElement.width
      this.imgHeightRatio = this.canvas.height / this.imgElement.height
      // 实例化背景图
      this.imgInstance = new fabric.Image(this.imgElement, {
        //设置图片在canvas中的位置和样子
        left: 0,
        top: 0,
        width: this.imgElement.width,
        height: this.imgElement.height,
        scaleX: this.canvas.width / this.imgElement.width,
        scaleY: this.canvas.height / this.imgElement.height,
        //angle:30//设置旋转
      });
      // 绑定画板事件
      _this.fabricObjAddEvent();
    },
    //画板监听,进行画图
    fabricObjAddEvent() {
      //按下鼠标
      this.canvas.on("mouse:down", (options) => {
        // 由原来的 options.e.clientX 改为 options.pointer.x
        var x = options.pointer.x;
        var y = options.pointer.y;
        this.firstPoint = { x: x, y: y };
        this.isDrawing = true;
        console.log("start", options.e.clientX, options.e.clientY);
      });
      // 移动鼠标
      this.canvas.on("mouse:move", function (options) {
        //var options = ev || window.event;
        //console.log("move", options.e.clientX, options.e.clientY)
      });
      // 当松开鼠标的时候把矩形框画出来
      this.canvas.on("mouse:up", (options) => {
        // 获得鼠标坐标
        var x = options.pointer.x;
        var y = options.pointer.y;
        this.lastPoint = { x: x, y: y };
        
        var rect = {};
        rect.xmin = this.firstPoint.x;
        rect.ymin = this.firstPoint.y;
        rect.width = this.lastPoint.x - this.firstPoint.x ;
        rect.height = this.lastPoint.y - this.firstPoint.y ;

        this.rects_list.push(rect);

        // 调用 darwRect进行画框
        this.drawRect(
          rect.xmin,
          rect.ymin,
          rect.width,
          rect.height
        );

        console.log("rets_list 值为 ", this.rects_list);
        //存入
        this.singleImg.rects_list = this.rects_list;
        console.log(
          "end",
          this.firstPoint.x,
          this.firstPoint.y,
          this.lastPoint.x,
          this.lastPoint.y
        );
        //console.log("up", options.e.clientX, options.e.clientY)
        //保存坐标信息
      });
    },
    //提交上一张图片信息进行保存
    saveLastImageInfo(lastImageInfo){
      console.log("saveLast ",lastImageInfo)
      // var imageInfo =  JSON.stringify(lastImageInfo);
      var n = {}
      n.url= lastImageInfo.url
      n.img_width_ratio = this.imgWidthRatio
      n.img_height_ratio = this.imgHeightRatio
      console.log("结果怎么是这样",lastImageInfo.img_width_ratio)
      n.rects_list = lastImageInfo.rects_list
      var jsonObj = JSON.stringify(n);
      // alert(jsonObj)
      //console.log("json字符串 ",n,jsonObj)
      //异步请求,保存图片信息，包括坐标和标签
      $.ajax({
        url: this.imgInfoUrl,
        type: "put",
        data: { user_name: "123", device_id: "123456",single_img_info:jsonObj },
        dataType: "json",
        success: function (data, dataTextStatus, jqxhr) {
          console.log("返回数据 ： ", data);
      
        },
        error: function (jqxhr, textStatus, error) {
          console.log("__失败__");
          console.log(error);
        
        },
      });

    },

    // 当点击下一张图片时设置背景图并画出矩形框
    //步骤：提交保存上一张图片---清空画板---加载图片和图片坐标信息
    setImgCanvas(url) {
      /**
       * 先保存上一张图片，再对当前图片画矩形
       */
    
      var _this = this;
      console.log("查看imgInfo有多少 ： ", _this.imgInfos);
      //首先获取到上一张图片url
      var lastUrl = _this.currentUrl
      //上一张的图片信息
      var lastImgInfo = {};
      console.log("上一次的url ",lastUrl,_this.rects_list.length)
      //空的都不进行保存，不允许把坐标情况
      if(typeof(lastUrl) !=  "undefined" && !(lastUrl===null) &&_this.rects_list.length>0){
        
        lastImgInfo.url = lastUrl;
        lastImgInfo.rects_list = _this.rects_list;
        
        var lastIndex = -1;
        //上一张索引
        lastIndex = _this.imgInfos.findIndex((imgObj, lastIndex) => {
            return imgObj.url === lastUrl;
          });
        //对上一张进行更新，先删除，后更新
        //根据索引先把图片删除掉
        _this.imgInfos.splice(lastIndex, 1);
            //对新图片进行保存
        _this.imgInfos.push(lastImgInfo);
        //保存图片信息到后台
        _this.saveLastImageInfo(lastImgInfo);

      }
      // 首先清空之前画布
      _this.canvas.clear();
      //处理逻辑：通过url 查找到对应的图片信息，根据信息判断
      //-1代表不存在
      console.log("当前url ",url)
      var curIndex = -1;
      curIndex = _this.imgInfos.findIndex(v=>v.url==url)
      //取矩形信息画图
      _this.rects_list = _this.imgInfos[curIndex]["rects_list"];
      console.log("当前索引rects_list ",_this.rects_list)
      //非空取出来画图
      if (_this.rects_list) {
            //如果图片中已经有矩形坐标
            var label_name = 'one'
            //绘制矩形
            for (let i = 0; i < _this.rects_list.length; i++) {
              var rect = _this.rects_list[i];
              var xmin = rect['xmin'];
              var ymin = rect['ymin']
              var width = rect['width']
              var height = rect['height']
              var label_name = rect['label'];
              console.log("strs.length", );
              _this.drawRectAndText(
                  label_name,
                  
                  parseFloat(xmin),
                  parseFloat(ymin),
                  parseFloat(width),
                  parseFloat(height)
                );
              // 添加标签,还没把没有标签的情形房间去考虑
             

              console.log("开始绘制了，准备");
              // this.drawRect(200,280,30,70);
            }
          }


     
      //*****************加载图片信息********************** */
      

      //###########加载背景图############
      
      //获取到
      _this.imgElement.src = url;
      //当前url
      _this.currentUrl = url;
      //需要把缩放比例进行保存 09-24
      this.imgWidthRatio = this.canvas.width / this.imgElement.width
      this.imgHeightRatio = this.canvas.height / this.imgElement.height
       //需要把缩放比例进行保存 09-24
      this.imgInstance = new fabric.Image(this.imgElement, {
        //设置图片在canvas中的位置和样子
        left: 0,
        top: 0,
        width: this.imgElement.width,
        height: this.imgElement.height,
        scaleX: this.imgWidthRatio,
        scaleY: this.imgHeightRatio ,
        //angle:30//设置旋转
      });
      //设置背景
      this.canvas.setBackgroundImage(this.imgInstance);

      //###########加载背景图############

    },
    // 画矩形
    drawRect(t, l, w, h) {
      // console.log("@@@@@@@@@@@@@@@@@@@", t, l, w, h);
      var rect = new fabric.Rect({
        top: l, //距离画布上边的距离
        left: t, //距离画布左侧的距离，单位是像素
        width: w, //矩形的宽度
        height: h, //矩形的高度
        fill: "#00000000",
        evented: false, //rect 无法被选中
        stroke: "red", // 边框原色
        strokeWidth: 3, // 边框大小
      });

      //添加矩形框
      this.canvas.add(rect);
    },
    onContextmenu(event) {
      console.log("右键");
      //阻止系统右键菜单
      event.preventDefault();
      var pointer = this.canvas.getPointer(event.originalEvent);
      //获取画布所有矩形目标
      var objects = this.canvas.getObjects();
      //遍历所有矩形目标
      for (var i = objects.length - 1; i >= 0; i--) {
        this.object = objects[i];
        //判断该对象是否在鼠标点击处
        if (this.canvas.containsPoint(event, this.object)) {
          //选中该对象
          this.canvas.setActiveObject(this.object);
          //显示菜单
          this.showContextMenu(event, this.object);
          
          //显示右击菜单，获取选中的key值，并且调用contextMenuClick
          $(".context-menu-root")
            .css("left", event.clientX)
            .css("top", event.clientY)
            .css("z-index", 99999999999)
            .show();
          continue;
        }
      }
      return false;
    },

    // 动态加载菜单
    loadMean(object) {
      
      var _this = this;
      // alert(_this.labels)
      //循环遍历标签数组加载标签项到右键菜单
      for (var i = 0; i < _this.labels.length; i++) {
        var obj = {};
        obj["name"] = _this.labels[i];
        obj["icon"] = "label";
        obj["data"] = object;
        // 加入到菜单
        _this.contextMenuItems[`label${i}`] = obj;
      }
    },

    //显示菜单内容
    showContextMenu(event, object) {
      let _this = this;
      //alert("显示菜单")
      //定义右键菜单项，默认菜单功能
      _this.contextMenuItems = {
        delete: { name: "删除", icon: "delete", data: object },
        add: { name: "新增标签", icon: "add", data: object },
      };

      //动态加载菜单
      _this.loadMean(object);
      //右键菜单显示位置
      _this.position = {
        x: event.clientX,
        y: event.clientY,
      };
     
      // 显示菜单
      $("#contextmenu-output").contextMenu(_this.position);
      
    },
    //右键点击菜单后的触发事件
    contextMenuClick(key, position) {
      let _this = this;
      console.log("key", key);
      // alert(this.key);
      if (key == "delete") {
        //let _this = this;
        //得到对应的object并删除
        var object = this.contextMenuItems[key].data;
        
  
        var temp_rect = {};
        temp_rect['xmin'] = object.left;
        temp_rect['ymin'] = object.top;
        temp_rect['width'] = object.width;
        temp_rect['height'] = object.height;


        var index = _this.rects_list.indexOf(temp_rect);
     
        _this.rects_list.splice(index, 1);
        //console.log("delete list",_this.rects_list)
        this.canvas.remove(object); //删除矩形框
      } else {
        console.log("输出的标签为: ", key, this.contextMenuItems);
        var new_key = key;
        console.log("根据key获得", this.contextMenuItems[new_key]);
        var label_name = this.contextMenuItems[key].name;
        console.log("根据key 获得的name ", label_name);
        // 把标签和坐标保存
        var object = this.contextMenuItems[key].data;
       
        var temp_rect = {};
        temp_rect['xmin'] = object.left;
        temp_rect['ymin'] = object.top;
        temp_rect['width'] = object.width;
        temp_rect['height'] = object.height;

         var temp_rect_label = {};
        temp_rect_label['xmin'] = object.left;
        temp_rect_label['ymin'] = object.top;
        temp_rect_label['width'] = object.width;
        temp_rect_label['height'] = object.height;
        temp_rect_label['label'] = label_name;


      
        var index = _this.rects_list.indexOf(temp_rect);
        console.log("删除之前的矩形信息", _this.rects_list);
        //删除矩形信息
        _this.rects_list.splice(index, 1);
        //重新添加矩形信息
        _this.rects_list.push(temp_rect_label);
        // console.log("查看更新标签后的矩形信息", _this.rects_list);

        var top = object.top;
        var left = object.left;
        var w = object.width;
        var h = object.height;
        this.drawRectAndText(label_name, left,top,  w, h);
        // console.log("label", key);
      }
    },

    drawRectAndText(label_name, left, top, w, h) {
      console.log("画框和标签接收到的 label",label_name)
      let _this = this;
      //1 文本框
      var text = new fabric.Text(label_name, {
        originX: "center",
        originY: "center",
        left: left - 4,
        top: top - 4,
        fill: "yellow",
      });

      // 2 矩形框
      var rect = new fabric.Rect({
        top: top, //距离画布上边的距离
        left: left, //距离画布左侧的距离，单位是像素
        width: w, //矩形的宽度
        height: h, //矩形的高度
        fill: "#00000000",
        evented: false, //rect 无法被选中
        stroke: "red", // 边框原色
        strokeWidth: 3, // 边框大小
      });

      //组合矩形和文本
      var group = new fabric.Group([rect, text]);

      //删除矩形框
      _this.canvas.remove(_this.canvas.getActiveObject());
      //3 添加矩形和文本信息
      _this.canvas.add(group);
    },

    getImginfo() {
      //发送ajax请求，将数据请求到放到imgInfos中,在munted中进行调用################################
      //##############################################
    },
    //打开标签栏进行标签添加和删除
    open() {
      var _this = this;
      this.$prompt("请输入标签", "新增标签", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        inputPattern: /^\S{1,10}$/,
        inputErrorMessage: "标签格式不正确",
      })
        .then(({ value }) => {
          _this.labels.push(value);
          //保存数据到后台
          _this.saveLabels(value);
          this.$message({
            type: "success",
            message: "你的标签是: " + value,
          });
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "取消输入",
          });
        });
    },
    //保存标签
    saveLabels(value) {
      // var save_label_url = "http://127.0.0.1:9999/src/labels";
      // alert("d");
      let _this = this;
      //后台请求数据
      $.ajax({
        url: _this.saveLabelUrl,
        type: "put",
        data: { user_name: "123", device_id: "123456",label:value },
        dataType: "json",
        success: function (data, dataTextStatus, jqxhr) {
          console.log("初始化返回数据 ： ", data);
          // _this.labels = data.data;
          // alert(data.data);
          // return data.data
        },
        error: function (jqxhr, textStatus, error) {
          console.log("__失败__");
          console.log(error);
        
        },
      });
    },
  },
};
</script>
<style lang="scss">
// @import "../../css/base.scss";
// @import "../../css/varis.scss";
body {
  position: relative;
}
.container {
  position: relative;
  height: 240px;
  width: 400px;
  margin: 10px 10px 0 10px;
  padding: 0;
  margin: 0 auto;
}
.canvas-container {
  position: absolute;
  left: 0;
  top: -189px;
  z-index: 9999 !important;
}
.upper-canvas {
  box-sizing: border-box;
  border: 1px solid #ccc;
  box-shadow: 5px 5px 3px #888888;
}
.swiper-container:nth-child(2) {
  width: 101%;
  height: 240px;
  margin-left: auto;
  margin-right: auto;
}
#sel {
  position: absolute;
  left: 100px;
  top: 100px;
  width: 60px;
  display: none;
  z-index: 999999 !important;
}
.swiper-container.first-wrapper {
  position: absolute;
  left: 0;
  top: 0;
  display: none !important;
  height: 0;
}
.swiper-slide {
  background-position: center;
}
.gallery-thumbs {
  display: absolute;
  left: 0;
  top: -185px;
}
.gallery-top {
  height: 80%;
  width: 100%;
}
.gallery-thumbs {
  height: 50%;
  box-sizing: border-box;
  padding: 10px 0;
  background-color: black;
  width: 500px;
}
.gallery-thumbs .swiper-slide {
  width: 25%;
  height: 80%;
  opacity: 0.4;
  background-size: 100% 100%;
}
.gallery-thumbs .swiper-slide-thumb-active {
  opacity: 1;
}
.context-menu-icon::before {
  position: absolute;
  top: 50%;
  left: 0;
  width: 2em;
  font-family: context-menu-icons;
  font-size: 1em;
  font-style: normal;
  font-weight: 400;
  line-height: 1;
  color: #2980b9;
  text-align: center;
  -webkit-transform: translateY(-50%);
  -ms-transform: translateY(-50%);
  -o-transform: translateY(-50%);
  transform: translateY(-50%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.context-menu-icon-delete:before {
  content: "\EA04";
}
.context-menu-icon-add:before {
  content: "\EA01";
}
.list_label {
  position: absolute;
  right: -368px;
  top: 10px;
  z-index: 99999;
  width: 200px;
  ul {
    list-style: none;
    text-align: center;
    border: 1px solid #ccc;
    box-shadow: 10px 5px 5px #ccc;
    li {
      list-style-type: none;
      &:nth-child(odd):hover {
        background-color: red;
        list-style: none;
      }
      &:nth-child(even):hover {
        background-color: green;
        list-style: none;
      }
      &:last-child {
        background-color: #ccc;
      }
    }
  }
}
.el-message-box__wrapper {
  z-index: 999999 !important;
}
</style>

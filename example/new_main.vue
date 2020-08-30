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
//import $ from "jquery";
import Swiper from "../../js/swiper-bundle.js";
export default {
  data() {
    return {
      name: "Jquery_contextmenu_44",
      banners: [
        { url: "../../images/avator.jpg" },
        { url: "../../images/4.jpg" },
        { url: "../../images/5.jpg" },
        { url: "../../images/6.jpg" },
        { url: "../../images/7.jpg" },
        { url: "../../images/8.jpg" },
        { url: "../../images/1.png" },
        { url: "../../images/2.png" },
        { url: "../../images/3.png" },
        { url: "../../images/4.png" },
        { url: "../../images/5.png" },
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
      singleImg: {},
      rects_list: [], //一个矩形框信息
      //lastImgInfo:[],//保存上一张图片信息
      labels: ["1", "2", "3"],
    };
  },
  created() {
    //从本地中加载数据   或 从数据库中获取数据
    if (localStorage.getItem("imgInfos")) {
      // this.imgInfos = JSON.parse(localStorage.getItem("imgInfos"));
    }
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
        //获取下面的img图片
        var imgurl = $(".swiper-slide-active img").attr("src"); //当前图片url地址，上一张图片的地址
        // console.log(imgurl)
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
    //添加右击事件并初始化
    onloadMenu() {
      //需要通过_this 方能获取到contextMenuItems,否则为未识别到
      let _this = this;
      //添加右击事件
      $(".upper-canvas").contextmenu(this.onContextmenu);
      //初始化右键菜单
      $.contextMenu({
        selector: "#contextmenu-output",
        trigger: "none",
        build: function ($trigger, e) {
          var item = _this.contextMenuItems;
          //构建菜单项build方法在每次右键点击会执行
          return {
            callback: _this.contextMenuClick,
            items: item,
          };
        },
      });
    },
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
      this.fabricObjAddEvent();
    },
    //画板监听
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
        // 调用 darwRect进行画框
        this.drawRect(
          this.firstPoint.x,
          this.firstPoint.y,
          this.lastPoint.x - this.firstPoint.x,
          this.lastPoint.y - this.firstPoint.y
        );

        //右键选择框弹出

        //var rect = new Array(this.firstPoint.x ,this.firstPoint.y,this.lastPoint.x - this.firstPoint.x,this.lastPoint.y - this.firstPoint.y);
        this.rects_list.push(
          this.firstPoint.x +
            "-" +
            this.firstPoint.y +
            "&" +
            (this.lastPoint.x - this.firstPoint.x) +
            "-" +
            (this.lastPoint.y - this.firstPoint.y)
        );

        //console.log(this.firstPoint.x+"-"+this.firstPoint.y+"&"+(this.lastPoint.x - this.firstPoint.x)+"-"+(this.lastPoint.y - this.firstPoint.y))
        console.log("rets_list 值为 ", this.rects_list);
        this.singleImg["rects_list"] = this.rects_list;
        console.log(
          "end",
          this.firstPoint.x,
          this.firstPoint.y,
          this.lastPoint.x,
          this.lastPoint.y
        );
        //console.log("up", options.e.clientX, options.e.clientY)
        //保存坐标信息
        // var singlerRect = {};
        // singlerRect.firstPoint = this.firstpoint;
        // singlerRect.lastPoint = this.lastPoint;
      });
    },
    setImgCanvas(url) {
      // this.drawRect(150,150,30,70);
      //console.log("%%%%%%%%%%%%%%%%%%%%%%%%%%%")
      var _this = this;
      console.log("查看imgInfo有多少 ： ", _this.imgInfos);
      // 首先清空之前画布
      _this.canvas.clear();
      console.log("上一张 ", _this.singleImg.url);
      //保存上一张图片信息
      var lastImgInfo = [];
      lastImgInfo["url"] = _this.singleImg.url;
      lastImgInfo["rects_list"] = _this.singleImg.rects_list;
      _this.singleImg = [];
      //把当前图片url 保存
      this.singleImg["url"] = url;
      //rects_list 默认为空
      this.singleImg["rects_list"] = [];
      //*****************加载图片信息********************** */
      //从imgInfo中加载图片信息
      //判断imgInfos中是否已经存在那张图片,如果存在取index,加载坐标信息，如果不在则把url 信息加载添加到imgInfos中
      if (_this.imgInfos.length == 0) {
        alert("首次加载");
        //第一次加载
        console.log("首次加载的url", _this.singleImg.url);
        _this.imgInfos.push(_this.singleImg);
        _this.rects_list = [];
        //将数据进行持久化，保存到本地或者数据库
        // localStorage.setItem("imgInfos", JSON.stringify(_this.imgInfos));
      } else {
        console.log("非首次加载进入", lastImgInfo.url);
        //判断上一张图片是否已保存，存在更新，不存在，保存起来
        var last_index = -1;
        if (_this.imgInfos.length > 0) {
          last_index = _this.imgInfos.findIndex((imgObj, last_index) => {
            return imgObj.url === lastImgInfo.url;
          });
        }
        console.log("需要保存的上一张图片信息 ", lastImgInfo);
        if (last_index == -1) {
          console.log("上次索引是-1");
          _this.imgInfos.push(lastImgInfo);
        } else {
          console.log("先删除图片在保存");
          if (lastImgInfo.rects_list.length != 0) {
            _this.imgInfos.splice(last_index, 1);
            _this.imgInfos.push(lastImgInfo);
          }

          //将数据进行持久化，保存到本地或者数据库
          //  localStorage.setItem("imgInfos", JSON.stringify(_this.imgInfos));
        }
        //如果不为0，先保存上一张图和坐标信息，取url,判断是否有框，有就画框

        _this.rects_list = [];
        var index = -1;
        if (_this.imgInfos.length > 0) {
          index = _this.imgInfos.findIndex((imgObj, index) => {
            return imgObj.url === url;
          });
        }

        console.log("获取index ", index);
        // 根据当前图片索引画框
        if (index != -1) {
          console.log("开始进入画框", _this.imgInfos[index]["rects_list"]);
          //则将该图片信息加载出来，再在图片上绘制矩形框
          if (_this.imgInfos[index]["rects_list"]) {
            //如果图片中已经有矩形坐标
            _this.rects_list = _this.imgInfos[index]["rects_list"];
            //绘制矩形
            for (let i = 0; i < _this.rects_list.length; i++) {
              var strs = _this.rects_list[i].split("&");
              var cords = strs[0].split("-");
              var rectWH = strs[1].split("-");
              console.log("strs.length",strs.length);
              // 添加标签,还没把没有标签的情形房间去考虑
              if(strs.length==3){
                
                var label_name = strs[2];
                 _this.drawRectAndText(label_name,
                //调了位置，不然矩形有问题
                parseFloat(cords[1]),
                parseFloat(cords[0]),
                parseFloat(rectWH[0]),
                parseFloat(rectWH[1])
              );

              }else{
                _this.drawRect(
                parseFloat(cords[0]),
                parseFloat(cords[1]),
                parseFloat(rectWH[0]),
                parseFloat(rectWH[1])
              );

              }
              
              console.log("开始绘制了，准备");
              // console.log("parseFloat(cords[0])",parseFloat(cords[0]))
              //  console.log("parseFloat(cords[1])",parseFloat(cords[1]))
              
              

              // this.drawRect(200,280,30,70);
            }
          }
        }

        //****************************************** */
      }

      //###########加载背景图############

      //获取到
      _this.imgElement.src = url;

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
      //设置背景
      this.canvas.setBackgroundImage(this.imgInstance);

      //###########加载背景图############

      //发送ajax请求将数据存储到后端数据库################################
      //##############################################

      // console.log("imginfo" + window.JSON.stringify(this.imgInfos)); //打印上一张图片时所有图片数量
    },
    // 画矩形
    drawRect(t, l, w, h) {
      console.log("@@@@@@@@@@@@@@@@@@@", t, l, w, h);
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
    loadMean(object){

      var _this = this;
      //循环遍历标签数组加载标签项到右键菜单
      for(var i=0;i<_this.labels.length;i++){
        var obj = {};
        obj["name"] = _this.labels[i];
        obj["icon"] =  "label";
        obj["data"] =  object;
        // 加入到菜单
        _this.contextMenuItems[`label${i}`] = obj;
      }

    },

    //显示菜单内容
    showContextMenu(event, object) {
      let _this = this;
      //定义右键菜单项，默认菜单功能
      this.contextMenuItems = {
        delete: { name: "删除", icon: "delete", data: object },
        add: { name: "新增标签", icon: "add", data: object },
      };
       
      //动态加载菜单
      this.loadMean(object);
      //右键菜单显示位置
      this.position = {
        x: event.clientX,
        y: event.clientY,
      };
      // 显示菜单
      $("#contextmenu-output").contextMenu(this.position);
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
        
        var temp_rect =
          object.left +
          "-" +
          object.top +
          "&" +
          object.width +
          "-" +
          object.height;

        var index = _this.rects_list.indexOf(temp_rect);
        //   var index = _this.rects_list.findIndex((gOimbj, index) => {
        //   return imgObj.url === this.singleImg.url;
        // });
        // console.log("index",index);
        _this.rects_list.splice(index, 1);
        //console.log("delete list",_this.rects_list)
        this.canvas.remove(object); //删除矩形框
      } else if (key == "label0") {
        console.log("输出的标签为: ",key,this.contextMenuItems);
        var new_key = key;
        console.log("根据key获得",this.contextMenuItems[new_key]);
        var label_name = this.contextMenuItems[key].name
        console.log('根据key 获得的name ',label_name);
        // 把标签和坐标保存
        var object = this.contextMenuItems[key].data;
        //没有标签的的矩形框
        var temp_rect =  object.left +
          "-" +
          object.top +
          "&" +
          object.width +
          "-" +
          object.height;

        //增加了标签的矩形框
        var temp_rect_label =  object.left +
          "-" +
          object.top +
          "&" +
          object.width +
          "-" +
          object.height +
          "&"+
          label_name;
        //获取到矩形所在的索引
        var index = _this.rects_list.indexOf(temp_rect);
        console.log("删除之前的矩形信息",_this.rects_list);
        //删除矩形信息
        _this.rects_list.splice(index, 1);
        //重新添加矩形信息
        _this.rects_list.push(temp_rect_label);
        console.log("查看更新标签后的矩形信息",_this.rects_list);
        //把矩形框和文本框画出来
        //1 文本框
        // var text = new fabric.Text(label_name, {
        //   originX: 'center',
        //   originY: 'center',
        //   left: object.left, 
        //   top: object.top,
        //   fill: 'red',
        //   });
        // 2 矩形框
        // var rect = new fabric.Rect({
        // top: object.top, //距离画布上边的距离
        // left:object.left, //距离画布左侧的距离，单位是像素
        // width: object.width, //矩形的宽度
        // height: object.height, //矩形的高度
        // fill: "#00000000",
        // evented: false, //rect 无法被选中
        // stroke: "red", // 边框原色
        // strokeWidth: 3, // 边框大小
        // });

        // var group = new fabric.Group(
        //   [rect, text]);

        // //删除矩形框
        // _this.canvas.remove(_this.canvas.getActiveObject());
        // //3 添加矩形和文本信息
        // _this.canvas.add(group);
        var top = object.top;
        var left = object.left;
        var w = object.width;
        var h = object.height
        this.drawRectAndText(label_name,top,left,w,h);
        console.log("label", key);
      }
    },

    drawRectAndText(label_name,l,t,w,h){
      let _this = this;
        //1 文本框
        var text = new fabric.Text(label_name, {
          originX: 'center',
          originY: 'center',
          left: t-4, 
          top: l-4,
          fill: 'yellow',
          });

          // 2 矩形框
        var rect = new fabric.Rect({
          top: l, //距离画布上边的距离
          left:t, //距离画布左侧的距离，单位是像素
          width: w, //矩形的宽度
          height: h, //矩形的高度
          fill: "#00000000",
          evented: false, //rect 无法被选中
          stroke: "red", // 边框原色
          strokeWidth: 3, // 边框大小
        });

        //组合矩形和文本
        var group = new fabric.Group(
          [rect, text]);

        //删除矩形框
        _this.canvas.remove(_this.canvas.getActiveObject());
        //3 添加矩形和文本信息
        _this.canvas.add(group);

    },


    getImginfo() {
      //发送ajax请求，将数据请求到放到imgInfos中,在munted中进行调用################################
      //##############################################
    },
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
  },
};
</script>
<style lang="scss">
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

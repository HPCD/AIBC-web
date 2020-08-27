<template>
  <div class="container">
    <!-- Swiper -->
    <div class="swiper-container gallery-top"></div>
    <!-- <div style="display:flex; ">
      
    </div>-->
    <canvas id="canvas" ref="canvas" width="400" height="350">这是浏览器不支持canvas时展示的信息</canvas>
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
      obj_list:[],
      currentImgUrl: "",
      imgInfos: {
        //用于存储图片信息{url:[]}
        
      },
      singleImg: {},
      rects_list: [], //一个矩形框信息
    };
  },
  created() {},
  mounted() {
    //  设置图片缩略图
    var galleryThumbs = new Swiper(".gallery-thumbs", {
      spaceBetween: 10,
      slidesPerView: 4,
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
        scaleX:this.canvas.width/this.imgElement.width,
        scaleY:this.canvas.height/this.imgElement.height
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
      var rect = new Array( this.firstPoint.x,this.firstPoint.y,this.lastPoint.x - this.firstPoint.x,this.lastPoint.y - this.firstPoint.y);
      this.rects_list.push(rect);
      console.log("rectrf",this.rects_list)
        console.log(
          "end",
          this.firstPoint.x,
          this.firstPoint.y,
          this.lastPoint.x,
          this.lastPoint.y
        );
        //console.log("up", options.e.clientX, options.e.clientY)
        //保存坐标信息
        var singlerRect = {};
        singlerRect.firstPoint = this.firstpoint;
        singlerRect.lastPoint = this.lastPoint;
      });
    },
    setImgCanvas(url) {
      // let _this = this;
      // console.log("url ",_this.imgElement.src)
      //获取到
      this.imgElement.src = url;
      this.canvas.clear();
      this.rects_list = []
      // console.log(
      //   "bg ",
      //   this.canvas.width / this.imgElement.width,
      //   this.imgElement.width,
      //   this.imgElement.height
      // );

      //自适应图片大小和画板一致
      this.imgInstance.scaleToWidth(this.canvas.getWidth());
      this.imgInstance.scaleToHeight(this.canvas.getHeight());
      //this.canvas.add(image);

      this.imgInstance = new fabric.Image(this.imgElement, {
        //设置图片在canvas中的位置和样子
        left: 0,
        top: 0,
        width: this.imgElement.width,
        height: this.imgElement.height,
        scaleX:this.canvas.width/this.imgElement.width,
        scaleY:this.canvas.height/this.imgElement.height
        //angle:30//设置旋转
      });
      //设置背景
      this.canvas.setBackgroundImage(this.imgInstance);
      //保存图片信息
      this.singleImg.url = this.currentImgUrl;
      this.currentImgUrl = "";
      
      
      //点击下一张图片，则保存上一张图片信息
      this.singleImg.rects = this.rects;
      console.log(this.singleImg);
      //判断imgInfos中是否已经存在那张图片
      // var index = this.imgInfos.findIndex((imgObj, index) => {
      //   return imgObj.url === this.singleImg.url;
      // });
      // if (index != -1 && this.singleImg.rects.length > 0) {
      //   this.imgInfos.splice(index, 1); //将原先的删除
      // }
      // this.imgInfos.push(this.singleImg); //保存上一张图片信息
      //发送ajax请求将数据存储到后端数据库################################

      //##############################################

      //再将数清空
      this.singleImg = {};
      this.rects = [];
      
      console.log(this.imgInfos.length);
    },

    // 画矩形
    drawRect(t, l, w, h) {
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
    //显示菜单内容
    showContextMenu(event, object) {
      let _this = this;
      //定义右键菜单项
      this.contextMenuItems = {
        delete: { name: "删除", icon: "delete", data: object },
        add: { name: "新增标签", icon: "add", data: object },
        label: { name: "标签", icon: "label", data: object },
      };
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
        let _this = this;
        //得到对应的object并删除
        var object = this.contextMenuItems[key].data;
        console.log("before delete list",_this.rects_list)
        console.log("dfdg",object.left,object.top,object.width,object.height);
        var temp_rect = new Array(object.left,object.top,object.width,object.height);
        var index = _this.rects_list.indexOf(temp_rect);
      //   var index = _this.rects_list.findIndex((gOimbj, index) => {
      //   return imgObj.url === this.singleImg.url;
      // });
        console.log("index",index);
        _this.rects_list.splice(index,1);
        console.log("delete list",_this.rects_list)
        this.canvas.remove(object); //删除矩形框
      } else if ((this.key = "label")) {
        alert(this.contextMenuItems[key].name);
        console.log("label", key);
      }
    },
    getImginfo() {
      //发送ajax请求，将数据请求到放到imgInfos中,在munted中进行调用################################
      //##############################################
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
</style>

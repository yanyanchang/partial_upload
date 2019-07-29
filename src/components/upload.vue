<template>
  <div class="upload-container">
    <div class="choice-file" @click="choiceFile">
      <button class="upload-button choice-file-button">选择文件</button>
      <input class="choice-file-input" type="file" @change="fileInputChangeHandle">
    </div>
    <button v-if="!autoUpload" class="upload-button" @click="upload">上传</button>
    <div class="upload-list">
      <li v-for="(file, index) in files" :key="index">
        <a>
          <span class="uploadicon icon-file " />
          <span class="file-name">{{ file.name }}</span>
          <span class="uploadicon icon-check-circle" v-if="file.status === 'success'"></span>
          <span class="uploadicon icon-delete" @click="delFile(index)" v-if="index != uploadFileIndex && file.status != 'success'" />
          <template v-if="index === uploadFileIndex && file.status != 'success' ">
            <span class="uploadicon icon-play-circle-fill" v-if="isPause && uploadPercent>5" @click="goOnUpload "></span>
            <span class="uploadicon icon-poweroff-circle-fill" v-if="!isPause && uploadPercent>5" @click="pauseUpload "></span>
            <div class="progress-bar" :style="'width:'+uploadPercent+'%'" >
              <div class="progress-bar-rate" />
            </div>
          </template>
        </a>
      </li>
    </div>
  </div>
</template>
<script>
import SparkMD5 from 'spark-md5'
import axios from 'axios'
import qs from 'qs'

export default {
  props: {
    autoUpload: {
      type: Boolean,
      default: true
    },
    chunkSize: {
      type: Number,
      default: 2097152
    },
    uploadCheckUrl: {
      type: String,
      default: ''
    },
    uploadUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      files: [],
      uploadFileIndex: -1,
      uploadFileInfo: {},
      uploadPercent: 0,
      isPause:false,
      pauseLoadIndex:-1
    }
  },
  methods: {
    getFileInfo(file, chunkSize) {
      return new Promise((resolver, reject) => {
        const blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice
        const chunks = Math.ceil(file.size / chunkSize)
        let currentChunk = 0
        const spark = new SparkMD5.ArrayBuffer()
        const fileReader = new FileReader()
        const uploadFileInfo = new Object()
        uploadFileInfo.name = file.name
        uploadFileInfo.size = file.size
        uploadFileInfo.shardCount = chunks // 总片数
        uploadFileInfo.shard = [] // 文件段
        for (var i = 0; i < uploadFileInfo.shardCount; i++) {
          const start = i * chunkSize
          const end = Math.min(file.size, start + chunkSize)
          uploadFileInfo.shard[uploadFileInfo.shard.length] = file.slice(start, end) // 保存分段
        }
        fileReader.onload = (e) => {
          spark.append(e.target.result)
          currentChunk++
          this.updateUploadPercent(currentChunk, chunks, true)
          if (currentChunk < chunks) {
            loadNext()
          } else {
            uploadFileInfo.hash = spark.end()
            return resolver(uploadFileInfo)
          }
        }

        fileReader.onerror = function() {
          return reject('oops, something went wrong.')
          // console.warn('oops, something went wrong.')
        }

        function loadNext() {
          const start = currentChunk * chunkSize
          const end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize
          fileReader.readAsArrayBuffer(blobSlice.call(file, start, end))
        }

        loadNext()
      })
    },
    choiceFile(event) {
      try {
        const fileInput = event.currentTarget.childNodes[1]
        fileInput.click()
      } catch (e) {}
    },
    fileInputChangeHandle(event) {
      const file = event.target.files[0]
      this.files.push(file)
      if (this.autoUpload) {
        this.uploadFileIndex = this.files.length -1
        this.uploadPercent = 0
        this.uploadHandle()
      }
    },
    delFile(index) {
      this.files.splice(index, 1)
    },
    uploadHandle() {
      this.getFileInfo(this.files[this.uploadFileIndex], this.chunkSize).then(r => {
        this.uploadFileInfo = r
        this.uploadCheck()
      })
    },
    uploadCheck() {
      axios.post(this.uploadCheckUrl, qs.stringify({
        hash: this.uploadFileInfo.hash
      }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }}).then((response) => {
        const index = response.data
        if (index != '') {
          this.uploadFile(Number(index))
        } else {
          this.uploadFile(0)
        }
      }).catch((error) => {
      })
    },
    uploadFile(loadIndex) {
      if(this.isPause) {
        this.pauseLoadIndex = loadIndex
        return
      }
      var form = new FormData()
      form.append('hash', this.uploadFileInfo.hash)
      form.append('name', this.uploadFileInfo.name)
      form.append('size', this.uploadFileInfo.size)
      form.append('shardCount', this.uploadFileInfo.shardCount)
      form.append('blob', this.uploadFileInfo.shard[loadIndex])
      form.append('sdIndex', loadIndex)

      axios.post(this.uploadUrl,
        form,
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }}).then((response) => {
        const index = Number(response.data) + 1
        if (index <= this.uploadFileInfo.shardCount) {
          this.uploadFile(index)
          this.updateUploadPercent(loadIndex+1, this.uploadFileInfo.shardCount, false)
        } else {
          this.uploadPercent = 0
          this.files[this.uploadFileIndex].status = 'success'
          this.$set(this.files, this.uploadFileIndex, this.files[this.uploadFileIndex])
          alert('上传完毕')
        }
      }).catch((error) => {
      })
    },
    updateUploadPercent(current, total, isRead) {
      let percent = 0
      if (isRead) {
        percent = parseInt(current / total * 0.05 * 100)
      } else {
        percent = 5 + parseInt(current / total * 0.95 * 100)
      }
      this.uploadPercent = percent
    },
    goOnUpload(){
      this.isPause = false
      this.uploadFile(this.pauseLoadIndex)
    },
    pauseUpload(){
      this.isPause = true
    }
  }
}
</script>
<style>
@font-face {font-family: "uploadicon";
  src: url('data:application/x-font-woff2;charset=utf-8;base64,d09GMgABAAAAAAQsAAsAAAAACRgAAAPdAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHEIGVgCDQAqEeIQoATYCJAMYCw4ABCAFhG0HcRvvB8gekiQlAQUUACggOWQQD9+P/Tr3GSoNkmhi6B41kWiWRKcTGt7Cpo0b8oaElfD/r037dKIQUrVZPdVcYkNCjDzKqvhN9WRuBQz/P/fzdXl8YHnt2Vwqw7ppPG7cgPJHNUlp4hf0P4xdXMbpBHpNi0DtFFU0gEqhrReIC96sB1VMpZQQQre05exaIJ6h6k5T3M4AeHI/Pn4hLlQgqRm0TQ/PC02Q8zniRQka/f/RsY0Cdn8GMHuRsQIU4iHXdAX5oRVIr3R2mS2gV7ckfY54fuD5iRcl/zvImGLeiiS9+r88QpIVlWigifoRfldY945tIgSfBxASnycQMl/FCIWvEpUKZa3HrEH8AZHHPs8IZH1eGtNovJDaL0Cm0ZK1g+ipPg1NC/2cQ873bVwwzb990cK2K1carl5tvH69+dq1wYagyWNEr3TlyrCmhbRm6mZoj1sY92nbKPmYBprq1MpZYI/O2OhF/sDGAl8a+mLp4f6a9QcDgBnQVv51H75M55JD/dhNR4K7mUX+1JitHZo2dtgYr7fM96EX+qFF/swC39awpJzY0jCfnvpYY/wX+Tb6LtgfFu2xfPnNIsOyD9HylD7Dti8P336xT9/kI/iQ7M8f2SGdbjMsXpjEPI5egS5eRJC/AjMgD8+HxLvu69cns1u0ntocEz36CXm2NPjgwUNvYz5E3fAa5HUDzP9UOoUqRqXQqUpKauj41Tmr4+makh8qzsYKXUYAHRg7+/Ts2EDvU2ToFFjrObd4t///TzjnTCWDrVPoYnSKGLvzfnSkyvqzI4/dXOmBlMpM5JloDOjWDBgO0JF1UY6L1Y1Ho5FHHhP+BYXg528fW7d7xlcVIwP4bzJ/AM6OAvVZr1tMYv8X7JpNReZq6lbE8uZKgWYV4iZzfoKi/8E26l5fkonasYRuEyEkXaYg6zaDLvgVqPqsQdNtHXotK967zxgREkUNLJkAIAzbBcmgv5ANO4su+LtQTXoLzXAg6HUU3ofsMxc8nS8SvURM2DAE80bByRlaifbi64h5gF0vRrkusYmIPbwXx0bFJKPFxEnEPrboGWiOkyQOc6LgwEXgbMRuF7BLFKzEKEVZJMmVFh3N5b1QlFFwAG2biNCTECaYwRAYz0jgxNndJXTq/esQZgPY6YklZSXaJoSoBz89FitKTA10schZq+xc7tJjILM4EgkH44gEDlgRMBB2PSTAXPnLrAgjSRRLi4BLmmjUjqsrihpf4rjKPdBLu2QLNwpRMkpOKSgl9J9YiNEWaeRFo53IOd6yxypMhK4lER+XMIiIAscVoCMn2D1cdv2QhBIAAAAA') format('woff2');
}
.uploadicon {
  font-family: "uploadicon" !important;
  font-size: 16px;
  font-style: normal;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.icon-check-circle:before {
  content: "\e77d";
}

.icon-file:before {
  content: "\e7bb";
}

.icon-delete:before {
  content: "\e7c3";
}

.icon-poweroff-circle-fill:before {
  content: "\e847";
}

.icon-play-circle-fill:before {
  content: "\e848";
}

.upload-button{
  display: inline-block;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
  -webkit-appearance: none;
  text-align: center;
  box-sizing: border-box;
  outline: none;
  margin: 0;
  transition: .1s;
  font-weight: 500;
  padding: 9px 15px;
  font-size: 12px;
  border-radius: 3px;
}
.choice-file{
  display: inline-block;
}
.choice-file-button{
  color: #fff;
  background-color: #409eff;
  border-color: #409eff;
}
.choice-file-input{
  display: none;
}

.upload-list {
  margin-top: 10px;
}
.upload-list li{
  list-style: none;
  font-size: 12px;

}
.upload-list li a{
  color: #606266;
  display: inline-block;
  padding: 3px 0 3px 0;
}
.upload-list li a:hover{
  background: #efefef;
}
.upload-list li .icon-file,.icon-del{
  font-size: 12px;
}
.upload-list li .file-name{
  display: inline-block;
  width: 300px;
  margin: 0 20px 0 10px ;
}
.progress-bar-rate{
  background-color: #409eff;
  height: 2px;
}
</style>


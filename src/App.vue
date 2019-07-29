<template>
  <div id="app">
    <upload upload-check-url="http://127.0.0.1:8089/api/upload_check" upload-url="http://127.0.0.1:8089/api/upload" />
  </div>
</template>

<script>
import Upload from './components/upload'
export default {
  name: 'App',
  components: {
    Upload
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
}
</style>

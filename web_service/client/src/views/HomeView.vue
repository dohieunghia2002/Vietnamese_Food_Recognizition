<template>
  <h2 class="heading">Hệ thống nhận dạng món ăn đặc sản Việt Nam</h2>

  <v-container style="margin-top: 1.5rem;">
    <v-row>
      <v-col cols="6" class="sidebar--left">
        <v-btn rounded="sm" variant="outlined" class="btn-upload">
          <label for="upload-img">
            <v-icon icon="mdi-camera"></v-icon>
          </label>
          <input type="file" id="upload-img" @change="getUploadedImg">
        </v-btn>

        <div class="img__container">
          <img id="cur-img" src="../assets/images/logo_ctu.png" alt="ảnh người dùng upload">
        </div>
      </v-col>

      <v-col cols="6" class="sidebar--right">
        <h3>
          Kết quả
        </h3>
        <p>Các thành phần nguyên liệu gồm: <strong>{{ ingredients_str }}</strong></p>
        <p>Món ăn trong ảnh là: <strong>{{ foodName }} - Đặc sản {{ province }}</strong></p>

        <br />
        <br />
        <h3>Gợi ý các món ăn khác:</h3>
        <p v-for="(name, index) in suggests" :key="index">{{ name }}</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      ingredients: [],
      ingredients_str: '',
      imageSrc: '',
      foodName: '',
      province: '',
      suggests: []
    }
  },

  methods: {
    async getUploadedImg() {
      const file = await document.getElementById('upload-img').files[0]

      const imgElement = await document.getElementById('cur-img')
      imgElement.src = URL.createObjectURL(file)

      const form = new FormData()
      form.append('file', file)
      const res = await axios.post('http://127.0.0.1:9999/api/predict', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      console.log(res.data);
      const temp = await res.data.detected_classes
      this.ingredients = [...new Set(temp)]
      this.ingredients_str = this.ingredients.join(', ');
      this.imageSrc = 'data:image/jpeg;base64,' + res.data.detected_image;
      imgElement.src = this.imageSrc
      this.foodName = await res.data.food_name
      this.province = await res.data.province
      this.suggests = await res.data.suggest_others
    }
  },
}
</script>

<style>
.heading {
  text-transform: uppercase;
  color: rgba(255, 0, 0, .9);
  text-align: center;
  line-height: 5rem;
}

/* .sidebar--left,
.sidebar--right {
  border: 2px solid red;
} */

.img__container {
  margin-top: 1rem;
  width: 100%;
}

#cur-img {
  width: 70%;
}
</style>
import Vue from 'nativescript-vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user_Email: "",
    API_URL: "http://210.107.198.174:8000",
    shelter_List : [],
    shelter_List_Near :[],
    CurrentPostType : true,
    ownerPost: {
      title : " ",
      dog_name : " ",
      lost_time : " ",
      lost_time1 : " ",
      dog_sex : 1,
      dog_type :" ",
      dog_age : 0,
      dog_feature:" ",
      remark:" ",
      phone_num:" ",
      image:" ",
      lat: 0,
      lng: 0,
      posted_time:" ",
      posted_due:" ",
  },
  FinderPost: {
    title : " ",
    dog_type :" ",
    dog_feature:"특징",
    phone_num:"010",
    image:"asdasd",
    lat: 0,
    lng: 0,
    find_time :" ",
    find_time1 : " ",
    posted_time:" ",
    posted_due:" ",
  },
},
  mutations: {

  },
  actions: {

  }
});
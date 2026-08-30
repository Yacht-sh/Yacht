<template lang="html">
  <div class="apps page">
    <transition
      name="slide"
      enter-active-class="animated slideInRight delay"
      leave-active-class="animated slideOutLeft"
    >
      <router-view />
    </transition>
  </div>
</template>

<script>
export default {
  name: "Applications"
};
</script>

<style lang="css"></style>
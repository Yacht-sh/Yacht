<template lang="html">
  <div class="images page">
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
export default {};
</script>

<style lang="css"></style>
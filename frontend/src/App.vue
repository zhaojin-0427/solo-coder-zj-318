<template>
  <div id="app-layout">
    <el-container style="height: 100vh">
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <div class="logo-icon">📷</div>
          <div class="logo-text">
            <div class="logo-title">家族回忆</div>
            <div class="logo-subtitle">共编平台</div>
          </div>
        </div>
        <el-menu
          :default-active="$route.path"
          class="nav-menu"
          router
          background-color="transparent"
          text-color="#8B7355"
          active-text-color="#8B4513"
        >
          <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-footer">
          <div class="flow-badge">
            <div class="flow-title">记忆传承</div>
            <div class="flow-items">
              <div class="flow-item">照片整理</div>
              <div class="flow-arrow">→</div>
              <div class="flow-item">人物补注</div>
              <div class="flow-arrow">→</div>
              <div class="flow-item">故事沉淀</div>
              <div class="flow-arrow">→</div>
              <div class="flow-item">家庭共编</div>
            </div>
          </div>
        </div>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <h2 class="page-current-title">
              <el-icon style="margin-right: 8px"><component :is="currentRouteIcon" /></el-icon>
              {{ currentRouteTitle }}
            </h2>
          </div>
          <div class="header-right">
            <el-tag effect="plain" round style="margin-right: 12px; background: #FEF3E2; color: #8B4513; border: none;">
              👨‍👩‍👧‍👦 李氏家族 · 三代共编
            </el-tag>
            <el-avatar style="background: linear-gradient(135deg, #8B4513, #D2691E);">家</el-avatar>
          </div>
        </el-header>
        <el-main class="main-content">
          <FlowSteps :current="currentStep" />
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Picture, User, Document, CircleCheck, DataAnalysis, Search
} from '@element-plus/icons-vue'
import FlowSteps from '@/components/FlowSteps.vue'

const route = useRoute()

const menuItems = [
  { path: '/photos', title: '照片归档', icon: 'Picture' },
  { path: '/persons', title: '人物关系补注', icon: 'User' },
  { path: '/clues', title: '人物线索管理', icon: 'Search' },
  { path: '/memories', title: '回忆片段整理', icon: 'Document' },
  { path: '/confirm', title: '家庭确认台', icon: 'CircleCheck' },
  { path: '/stats', title: '数据统计', icon: 'DataAnalysis' }
]

const currentRouteTitle = computed(() => route.meta?.title || '首页')
const currentRouteIcon = computed(() => route.meta?.icon || 'Picture')
const currentStep = computed(() => route.meta?.step || 1)
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #3D2914 0%, #5C3A1E 50%, #8B4513 100%);
  padding: 20px 0;
  display: flex;
  flex-direction: column;
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 20px 24px;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: rgba(255,255,255,0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.logo-text {
  color: #FFF8F0;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}

.logo-subtitle {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 2px;
}

.nav-menu {
  border: none !important;
  margin-top: 16px;
  flex: 1;
}

.nav-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 12px;
  border-radius: 8px;
  color: rgba(255, 248, 240, 0.7);
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(255,255,255,0.1);
  color: #FFF8F0;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #F4A460, #D2691E);
  color: white;
  font-weight: 600;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.flow-badge {
  background: rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 16px;
  color: #FFF8F0;
}

.flow-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
  opacity: 0.9;
}

.flow-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.flow-item {
  font-size: 12px;
  opacity: 0.75;
  padding: 4px 8px;
  background: rgba(255,255,255,0.06);
  border-radius: 4px;
}

.flow-arrow {
  text-align: center;
  font-size: 12px;
  opacity: 0.5;
}

.header {
  background: #fff;
  border-bottom: 1px solid #E8D8C4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 64px;
}

.page-current-title {
  font-size: 20px;
  font-weight: 600;
  color: #8B4513;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.main-content {
  background: linear-gradient(135deg, #FFF8F0 0%, #FFFAF0 100%);
  overflow-y: auto;
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

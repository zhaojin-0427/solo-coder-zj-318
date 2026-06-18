<template>
  <div class="flow-steps">
    <div
      v-for="(step, index) in steps"
      :key="step.id"
      class="flow-step"
      :class="{ active: current === step.id, done: current > step.id }"
    >
      <div class="flow-step-icon">
        <el-icon v-if="current > step.id"><Check /></el-icon>
        <span v-else>{{ step.id }}</span>
      </div>
      <div class="flow-step-text">
        <div class="flow-step-label">{{ step.label }}</div>
        <div class="flow-step-desc">{{ step.desc }}</div>
      </div>
      <div v-if="index < steps.length - 1" class="flow-arrow">
        <el-icon><ArrowRight /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Check, ArrowRight } from '@element-plus/icons-vue'

defineProps({
  current: { type: Number, default: 1 }
})

const steps = [
  { id: 1, label: '照片整理', desc: '年代·场景·来源' },
  { id: 2, label: '采集任务', desc: '分派·认领·补注' },
  { id: 3, label: '线索认领', desc: '暂用名·待确认' },
  { id: 4, label: '人物补注', desc: '亲属·称呼·备注' },
  { id: 5, label: '故事沉淀', desc: '回忆·片段·关联' },
  { id: 6, label: '家庭共编', desc: '确认·投票·共识' },
  { id: 7, label: '数据统计', desc: '贡献·进度·排行' }
]
</script>

<style scoped>
.flow-steps {
  display: flex;
  align-items: stretch;
  background: #fff;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.08);
  margin-bottom: 24px;
  gap: 8px;
}

.flow-step {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s;
}

.flow-step.active {
  background: linear-gradient(135deg, #FEF3E2, #FFE4C4);
}

.flow-step.active .flow-step-icon {
  background: linear-gradient(135deg, #8B4513, #D2691E);
  color: white;
}

.flow-step.active .flow-step-label {
  color: #8B4513;
  font-weight: 700;
}

.flow-step.done .flow-step-icon {
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
}

.flow-step.done .flow-step-label {
  color: #059669;
}

.flow-step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #F5EDE0;
  color: #8B7355;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
  transition: all 0.3s;
}

.flow-step-text {
  flex: 1;
  min-width: 0;
}

.flow-step-label {
  font-size: 14px;
  font-weight: 600;
  color: #8B7355;
  transition: all 0.3s;
}

.flow-step-desc {
  font-size: 12px;
  color: #B5A48C;
  margin-top: 2px;
}

.flow-arrow {
  margin: 0 8px;
  color: #D4A574;
  font-size: 20px;
  align-self: center;
  flex-shrink: 0;
}
</style>

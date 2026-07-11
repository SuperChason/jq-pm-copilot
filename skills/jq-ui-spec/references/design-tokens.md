# 设计令牌

## CSS 变量

    :root {
      --color-primary: #3E5BF2;
      --color-primary-hover: #5B75FF;
      --color-primary-active: #2842D9;
      --color-primary-soft: #F0F2FF;
      --color-success: #52C41A;
      --color-warning: #FAAD14;
      --color-error: #F5222D;
      --color-info: #1890FF;
      --color-text-primary: #1A1A1A;
      --color-text-secondary: #6E6E73;
      --color-text-tertiary: #A0A0A5;
      --color-text-disabled: #CCCCCC;
      --color-border: #E5E5E5;
      --color-divider: #F0F0F0;
      --color-bg: #F5F5F7;
      --color-surface: #FFFFFF;
      --color-bg-tertiary: #F9F9FA;
      --color-table-header-bg: #F5F7FA;
      --color-table-header-text: #6E6E73;
      --color-table-row-hover: #F9F9FA;
      --sidebar-bg: #3E5BF2;
      --sidebar-text: #FFFFFF;
      --sidebar-text-secondary: rgba(255, 255, 255, 0.75);
      --sidebar-hover-bg: rgba(255, 255, 255, 0.10);
      --sidebar-active-bg: rgba(255, 255, 255, 0.15);
      --sidebar-active-text: #FFFFFF;
      --spacing-xs: 4px;
      --spacing-sm: 8px;
      --spacing-md: 16px;
      --spacing-lg: 24px;
      --spacing-xl: 32px;
      --radius-sm: 2px;
      --radius-base: 4px;
      --radius-lg: 6px;
      --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.08);
      --shadow-base: 0 2px 8px rgba(0, 0, 0, 0.12);
      --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.16);
      --header-height: 60px;
      --sidebar-width: 200px;
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      --font-size-xs: 12px;
      --font-size-sm: 13px;
      --font-size-base: 14px;
      --font-size-md: 16px;
      --font-size-lg: 18px;
      --font-size-xl: 20px;
      --font-size-xxl: 24px;
      --line-height-base: 1.5;
    }

## 使用规则

- 新页面优先引用令牌，避免新增近似颜色和间距。
- 主色用于主操作、当前状态和关键链接，避免大面积铺色。
- 危险操作使用错误色，并在提交前增加明确确认。
- 间距以 4px 为最小步进，常用 8、16、24、32px。
- 字号以 14px 为正文，12px 仅用于辅助信息且保证可读。
- 阴影用于表达层级，卡片优先用边框和轻阴影。

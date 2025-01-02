from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.styles import Style

# 定义可选字段
AVAILABLE_FIELDS = {
    'order_id': '订单号',
    'name': '货物名称',
    'quantity': '数量',
    'amount': '金额',
    'date': '日期',
    'status': '状态'
}

# 定义样式
style = Style.from_dict({
    'dialog': 'bg:#4444ff #ffffff',
    'dialog.body': 'bg:#000000 #ffffff',
    'dialog.border': '#00ff00',
    'selected': 'bg:#ffffff #000000',
    'checkbox': '#ffff00',
})

def select_fields():
    """显示交互式字段选择菜单"""
    try:
        # 准备选项列表
        values = [(key, value) for key, value in AVAILABLE_FIELDS.items()]
        
        # 显示复选框对话框
        result = checkboxlist_dialog(
            title='字段选择',
            text='请选择您需要抓取的数据字段（使用空格键多选，回车确认）:',
            values=values,
            style=style
        ).run()
        
        if not result:
            print("未选择任何字段，请重新选择")
            return None
            
        # 返回选中的字段
        selected_fields = {key: AVAILABLE_FIELDS[key] for key in result}
        print("\n已选择的字段:")
        for key, value in selected_fields.items():
            print(f"- {value}")
            
        return selected_fields
        
    except KeyboardInterrupt:
        print("\n已取消选择")
        return None
    except Exception as e:
        print(f"\n选择过程出错: {str(e)}")
        return None

def get_field_selectors():
    """返回字段对应的CSS选择器"""
    return {
        'order_id': '.order-id',
        'name': '.name',
        'quantity': '.quantity',
        'amount': '.amount',
        'date': '.date',
        'status': '.status'
    }

def format_field_value(field, value):
    """格式化字段值"""
    if not value:
        return "无数据"
        
    if field == 'amount':
        # 移除金额中的货币符号并转换为浮点数
        try:
            return float(value.replace('￥', '').strip())
        except:
            return value
    elif field == 'quantity':
        # 提取数量中的数字
        try:
            return int(value.strip())
        except:
            return value
    else:
        return value.strip()

def display_results(results):
    """显示抓取结果"""
    if not results:
        print("\n未获取到任何数据")
        return
        
    print("\n抓取结果:")
    for item in results:
        print("\n订单数据:")
        for field, value in item.items():
            print(f"- {AVAILABLE_FIELDS[field]}: {value}")
            
def handle_error(error, retry_callback=None):
    """处理错误并提供重试选项"""
    print(f"\n错误: {str(error)}")
    if retry_callback and input("\n是否重试？(y/n) ").lower() == 'y':
        return retry_callback()
    return None 
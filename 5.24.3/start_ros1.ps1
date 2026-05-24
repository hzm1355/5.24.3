# 深基坑巡检系统 - Windows PowerShell 启动脚本

# 颜色定义
$RED = "`e[0;31m"
$GREEN = "`e[0;32m"
$YELLOW = "`e[1;33m"
$NC = "`e[0m" # No Color

Write-Host "${GREEN}========================================${NC}"
Write-Host "${GREEN}  深基坑机器人巡检系统 - ROS1 启动器${NC}"
Write-Host "${GREEN}========================================${NC}"

# 检查ROS环境
if (-not $env:ROS_DISTRO) {
    Write-Host "${RED}错误: ROS环境未激活${NC}"
    Write-Host "请先运行: C:\opt\ros\noetic\x64\setup.bat"
    exit 1
}

Write-Host "${YELLOW}ROS版本: $env:ROS_DISTRO${NC}"

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 启动roscore (如果未运行)
$roscoreProcess = Get-Process roscore -ErrorAction SilentlyContinue
if (-not $roscoreProcess) {
    Write-Host "${YELLOW}启动 roscore...${NC}"
    Start-Process -FilePath "roscore" -NoNewWindow
    Start-Sleep -Seconds 3
} else {
    Write-Host "${GREEN}roscore 已在运行${NC}"
}

# 启动TF静态发布 (世界坐标系)
Write-Host "${YELLOW}发布静态TF...${NC}"
Start-Process -FilePath "rosrun" -ArgumentList "tf static_transform_publisher 0 0 0 0 0 0 world map 100" -NoNewWindow

# 启动机器人状态发布器
Write-Host "${YELLOW}启动机器人状态发布器...${NC}"
Start-Process -FilePath "rosrun" -ArgumentList "robot_state_publisher robot_state_publisher" -NoNewWindow

# 启动可视化节点
Write-Host "${YELLOW}启动可视化数据节点...${NC}"
$vizScript = Join-Path $ScriptDir "deep_pit_visualization.py"
$vizProcess = Start-Process -FilePath "python" -ArgumentList $vizScript -PassThru -NoNewWindow

# 等待节点启动
Start-Sleep -Seconds 2

# 检查话题
Write-Host "${YELLOW}`n可用话题列表:${NC}"
rostopic list | Select-String -Pattern "(trajectory|surfel|support|pit|laser|odometry|current_pose)"

# 启动RViz
Write-Host "${GREEN}`n启动 RViz...${NC}"
$rvizConfig = Join-Path $ScriptDir "robot_config.rviz"
Start-Process -FilePath "rviz" -ArgumentList "-d $rvizConfig" -NoNewWindow

# 等待RViz关闭
Write-Host "${YELLOW}`n按 Ctrl+C 关闭所有节点...${NC}"
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "${YELLOW}`n关闭所有节点...${NC}"
    if ($vizProcess -and -not $vizProcess.HasExited) {
        Stop-Process -Id $vizProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Name "static_transform_publisher" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "robot_state_publisher" -Force -ErrorAction SilentlyContinue
    Write-Host "${GREEN}已关闭${NC}"
}

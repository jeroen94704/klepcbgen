$Comp
L Switch:SW_Push K{{num}}
U 1 1 KEYSWITCH_{{num}}
P {{x+200}} {{y}}
F 0 "K{{num}}" H {{x+200}} {{y + 233}} 60  0000 C CNN
F 1 "KEYSW" H {{x+200}} {{y-100}} 60  0001 C CNN
F 2 "Button_Switch_Keyboard:SW_Cherry_MX_{{keywidth}}u_PCB" H {{x+200}} {{y}} 60  0001 C CNN
F 3 "" H {{x+200}} {{y}} 60  0000 C CNN
	1    {{x+200}} {{y}}
	1    0    0    -1  
$EndComp
$Comp
L Device:D D{{num}}
U 1 1 DIODE_{{num}}
P {{x+400}} {{y+150}}
F 0 "D{{num}}" V {{x+500}} {{y+150}} 60  0000 R CNN
F 1 "D" V {{x+150}} {{y+100}} 60  0001 R CNN
F 2 "Diode_SMD:D_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H {{x}} {{y+150}} 60  0001 C CNN
F 3 "" H {{x}} {{y+150}} 60  0000 C CNN
	1    {{x+400}} {{y+150}} 
	0    -1   -1   0   
$EndComp
Text Label {{x+400}}  {{y+300}} 0    50   ~ 0
Row_{{rowNum}}
Text Label {{x}}  {{y}} 2    50   ~ 0
Col_{{colNum}}

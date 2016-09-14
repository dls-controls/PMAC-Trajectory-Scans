; *****************************************************************************************
; Variables
; *****************************************************************************************

; Change these values for your PMAC
#define BlankAdr0           30000           ; Start of user buffer defined on PMAC
#define AxisAdr             30010           ; BlankAdr + 10 - Location of axes bit mask
#define BufferAdr           30020           ; BlankAdr + 20 - Start of points buffers
#define BuffLen             1000
#define ProgramNum          1
#define VersionNum          1.1

; EPICS Required Variables

#define Status              P4001           ; Status of motion program for EPICS
                                                    ; 0: Initialised, 1: Active, 2: Idle, 3: Error
#define Abort               P4002           ; Abort trigger for EPICS
#define Axes                P4003           ; An int between 1 and 511 specifying which axes to use
#define BufferLength        P4004           ; Length of a single buffer e.g. AX, AY...
#define TotalPoints         P4005           ; Total number of points scanned through

#define CurrentIndex        P4006           ; Current index position in buffer
#define CurrentBuffer       P4007           ; Current buffer specifier - 0: A, 1: B

#define BufferAdr_A         P4008           ; Start index of buffer A
#define BufferAdr_B         P4009           ; Start index of buffer B
#define CurrentBufferAdr    P4010           ; A or B buffer address
 
#define BufferFill_A        P4011           ; Fill level of buffer A
#define BufferFill_B        P4012           ; Fill level of buffer B
#define CurrentBufferFill   P4013           ; A or B buffer fill level
#define PrevBufferFill      P4014           ; Fill level of previous buffer
#define Error               P4015           ; Error code  0: No error, 1: Invalid axes value,
                                            ; 2: Move time of 0, 3: Following error/ Run-time error
#define Version             P4020           ; Version number for motion program
Version = VersionNum

; Motion Program Variables
; ************************

#define Prev_A              P4101           ; Previous coordinates for velocity calculations
#define Prev_B              P4102  
#define Prev_C              P4103  
#define Prev_U              P4104  
#define Prev_V              P4105  
#define Prev_W              P4106  
#define Prev_X              P4107  
#define Prev_Y              P4108  
#define Prev_Z              P4109  

#define Time                P4110           ; Current coordinate values
#define Current_A           Q71
#define Current_B           Q72
#define Current_C           Q73
#define Current_U           Q74
#define Current_V           Q75
#define Current_W           Q76
#define Current_X           Q77
#define Current_Y           Q78
#define Current_Z           Q79
#define User                P4120
#define VelMode             P4121

#define A_Vel               P4131          ; Previous coordinate values
#define B_Vel               P4132
#define C_Vel               P4133
#define U_Vel               P4134
#define V_Vel               P4135
#define W_Vel               P4136
#define X_Vel               P4137
#define Y_Vel               P4138
#define Z_Vel               P4139

#define CalculatedBase      P4140           ; Calculated temporary variable for Current base address
#define TmpTime             P4141           ; Calculated temporary variable for time in velocity calcs

; Address-Based Variables
; ***********************

#define Trigger             M32

#define Next_Time           M4000                   ; Next coordinate for velocity calculations
#define Next_A              M4001                   ; These are incremented by changing *_Adr
#define Next_B              M4002
#define Next_C              M4003
#define Next_U              M4004
#define Next_V              M4005
#define Next_W              M4006
#define Next_X              M4007
#define Next_Y              M4008
#define Next_Z              M4009
#define Next_User           M4010
#define NextVelMode         M4011

NextVelMode->X:$BlankAdr0,4,4                        ; Set initial pointers and type
Next_User->X:$BlankAdr0,0,4
Next_Time->Y:$BlankAdr0,0,24

#define Time_Adr            M4020                   ; Pointers to Next_* coordinate addresses
#define A_Adr               M4021
#define B_Adr               M4022
#define C_Adr               M4023
#define U_Adr               M4024
#define V_Adr               M4025
#define W_Adr               M4026
#define X_Adr               M4027
#define Y_Adr               M4028
#define Z_Adr               M4029
#define User_Adr            M4030
#define VelMode_Adr         M4031

Time_Adr->Y$4FA0,0,24                               ; Assignments for pointers to M address locations
A_Adr->Y:$4FA1,0,24                                 ; M0 = $4000 -> M4000 = $4FA0
B_Adr->Y:$4FA2,0,24
C_Adr->Y:$4FA3,0,24
U_Adr->Y:$4FA4,0,24
V_Adr->Y:$4FA5,0,24
W_Adr->Y:$4FA6,0,24
X_Adr->Y:$4FA7,0,24
Y_Adr->Y:$4FA8,0,24
Z_Adr->Y:$4FA9,0,24
User_Adr->Y:$4FAA,0,24
VelMode_Adr->Y:$4FAB,0,24

#define AxesParser          M4040                   ; Specifiers for what axes are activated
#define A_Axis              M4041
#define B_Axis              M4042
#define C_Axis              M4043
#define U_Axis              M4044
#define V_Axis              M4045
#define W_Axis              M4046
#define X_Axis              M4047
#define Y_Axis              M4048
#define Z_Axis              M4049

AxesParser->Y:$AxisAdr,0,24                         ; Pointers to bits of Axes value
A_Axis->Y:$AxisAdr,0
B_Axis->Y:$AxisAdr,1
C_Axis->Y:$AxisAdr,2
U_Axis->Y:$AxisAdr,3
V_Axis->Y:$AxisAdr,4
W_Axis->Y:$AxisAdr,5
X_Axis->Y:$AxisAdr,6
Y_Axis->Y:$AxisAdr,7
Z_Axis->Y:$AxisAdr,8

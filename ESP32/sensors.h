
typedef struct { 
    char temp;
    char hum;
    float pres;
    float co2; 
} THCP;

typedef struct { 
    float rms;
    float ampx;
    float frecx;
    float ampy;
    float frecy;
    float ampz;
    float frecz;
} ACC_KPI; 

typedef struct {
    char batt;
    long timestamp; 
} BATT_TIME; 

typedef struct {
    float* acc_x;
    float* acc_y;
    float* acc_z;
} ACC;

void read_batt_time(BATT_TIME* dest);
void read_thcp_sensor(THCP* thcp);
void read_acc_kpi_sensor(ACC_KPI* kpi);
void read_accelerometer(ACC* acc);
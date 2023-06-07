#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <sys/time.h>
#include "esp_random.h"
#include "sensors.h"

// THPC constants
char MIN_TEMP = 5;
char MAX_TEMP = 30;
char MIN_HUM = 30;
char MAX_HUM = 80;
float MIN_PRES = 1000;
float MAX_PRES = 1200;
float MIN_CO2 = 30;
float MAX_CO2 = 200;

//Accelerometer KPI range
float MIN_AMP_X = 0.0059;
float MAX_AMP_X = 0.12;
float MIN_FREC_X = 29;
float MAX_FREC_X = 31;

float MIN_AMP_Y = 0.0041;
float MAX_AMP_Y = 0.11;
float MIN_FREC_Y = 59;
float MAX_FREC_Y = 61;

float MIN_AMP_Z = 0.008;
float MAX_AMP_Z = 0.15;
float MIN_FREC_Z = 89;
float MAX_FREC_Z = 91;

float get_rand(float min_val, float max_val){
    return min_val + (max_val-min_val) * (float) esp_random() / (float) UINT32_MAX;
}

void read_thcp_sensor(THCP* thcp){
    struct timeval tm; 
    gettimeofday(&tm,NULL);

    // Generating structure to store values

    // Temperature vals
    thcp->temp = (char) get_rand(MIN_TEMP, MAX_TEMP);

    // Humidity vals
    thcp->hum = (char) get_rand(MIN_HUM,MAX_HUM);

    // Pressure vals
    thcp->pres = get_rand(MIN_PRES, MAX_PRES);

    // CO2 vals
    thcp->co2 = get_rand(MIN_CO2, MAX_CO2);  
}

void read_acc_kpi_sensor(ACC_KPI* kpi){
    //Setting random seed
    srand(time(NULL));
    
    float ampx = get_rand(MIN_AMP_X, MAX_AMP_X);
    kpi->ampx = ampx;
    kpi->frecx = get_rand(MIN_FREC_X, MAX_FREC_X);

    float ampy = get_rand(MIN_AMP_Y, MAX_AMP_Y);
    kpi->ampy = ampy;
    kpi->frecy = get_rand(MIN_FREC_Y, MAX_FREC_Y);

    float ampz = get_rand(MIN_AMP_Z, MAX_AMP_Z);
    kpi->ampz = ampz;
    kpi->frecz = get_rand(MIN_FREC_Z, MAX_FREC_Z);

    kpi->rms = sqrt(ampx*ampx + ampy*ampy + ampz*ampz);
}

void read_batt_time(BATT_TIME* dest){
    struct timeval tm; 
    gettimeofday(&tm, NULL);
    dest->batt = (char) get_rand(0,100);
    dest->timestamp = (long) tm.tv_sec + (long) get_rand(1,10000);
}

void read_accelerometer(ACC* acc){
    int samples = 2000;
    acc->acc_x = malloc(samples*sizeof(float));
    acc->acc_y = malloc(samples*sizeof(float));
    acc->acc_z = malloc(samples*sizeof(float));   
    for(int i=0; i<samples; i++){
        acc->acc_x[i] = 2*sin(2*M_PI*0.001*i);
        acc->acc_y[i] = 3*cos(2*M_PI*0.001*i);
        acc->acc_z[i] = 10*sin(2*M_PI*0.001*i);
    }
}


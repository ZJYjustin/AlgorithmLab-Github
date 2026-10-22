// C++ 示例：使用本项目自己的 C/C++ 记录接口。
#include "algorithm_lab_c.h"
#include <iostream>

int main(void) {
    int allocation[5][3]={{0,1,0},{2,0,0},{3,0,2},{2,1,1},{0,0,2}};
    int maximum[5][3]={{7,5,3},{3,2,2},{9,0,2},{2,2,2},{4,3,3}};
    int work[3]={3,3,2}; /* 尝试改为 {0,0,0} */
    int need[5][3],finish[5]={0},sequence[5],count=0,i,j;
    char message[160];
    for(i=0;i<5;i++)for(j=0;j<3;j++)need[i][j]=maximum[i][j]-allocation[i][j];
    lab_create("need","Array2DTracer","Need · A / B / C");
    lab_create("allocation","Array2DTracer","Allocation · A / B / C");
    lab_create("work","Array1DTracer","Work · A / B / C");
    lab_create("finish","Array1DTracer","Finish");
    lab_create("seq","Array1DTracer","安全序列 · 进程编号");
    lab_create("log","LogTracer","检查过程");
    lab_array2d("need",&need[0][0],5,3);lab_array2d("allocation",&allocation[0][0],5,3);
    lab_array1d("work",work,3);lab_array1d("finish",finish,5);lab_array1d("seq",sequence,0);
    lab_log("log","开始安全性检查。");lab_step(__LINE__);
    while(count<5){
        int progressed=0;
        for(i=0;i<5;i++){
            int can_finish=1;
            if(finish[i])continue;
            for(j=0;j<3;j++)if(need[i][j]>work[j])can_finish=0;
            lab_row("need",i,0,2,1);
            snprintf(message,sizeof(message),"检查 P%d：%s",i,can_finish?"可以完成":"资源不足，跳过");
            lab_log("log",message);lab_step(__LINE__);
            if(can_finish){
                for(j=0;j<3;j++)work[j]+=allocation[i][j];
                finish[i]=1;sequence[count++]=i;progressed=1;
                lab_array1d("work",work,3);lab_array1d("finish",finish,5);lab_array1d("seq",sequence,count);
                snprintf(message,sizeof(message),"P%d 模拟完成并释放资源。",i);
                lab_log("log",message);lab_step(__LINE__);
            }
            lab_row("need",i,0,2,0);
        }
        if(!progressed)break;
    }
    lab_log("log",count==5?"安全：找到完整安全序列。":"不安全：找不到完整安全序列。不等于已发生死锁。");lab_step(__LINE__);
    std::cout << "safe=" << (count==5) << " sequence=";
    for(i=0;i<count;i++) std::cout << sequence[i] << " ";
    return 0;
}

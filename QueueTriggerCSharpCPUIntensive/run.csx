using System;
using System.Net;

public static long FindPrimeNumber(int n)
{
    int count=0;
    long a = 2;
    while(count<n)
    {
        long b = 2;
        int prime = 1;// to check if found a prime
        while(b * b <= a)
        {
            if(a % b == 0)
            {
                prime = 0;
                break;
            }
            b++;
        }
        if(prime > 0)
        {
            count++;
        }
        a++;
    }
    return(--a);
}

[return: Queue("outqueue")]
public static string Run(string myQueueItem, TraceWriter log)
{
    log.Info($"C# Queue trigger function processed: {myQueueItem}");

    int numInt = Convert.ToInt32(myQueueItem);
    long nthPrime = FindPrimeNumber(numInt);

    return numInt + "," + nthPrime;
}



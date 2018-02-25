using System;
    
[return: Queue("outqueue")]
public static string Run(string myQueueItem, TraceWriter log)
{
    log.Info($"C# Queue trigger function processed: {myQueueItem}");
    return myQueueItem;
}


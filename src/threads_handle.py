def finish_threads(threads_list):
    print(f"Working threads: {len(threads_list)}")
    print("Waiting for threads to finish")
    for threads in threads_list:
        try:
            threads.join()
        except (AttributeError, OSError) as e:
            print(e)
            return 1
        else:
            print(f"{threads}: finished")
            threads_list.remove(threads)
            print(f"Remaining threads: {len(threads_list)}")
    print("All threads have finished")

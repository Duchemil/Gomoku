# Gomoku

Ressources : 
Big : 2019 Heuristic for minimax gomoku : https://dr.lib.iastate.edu/server/api/core/bitstreams/39a805d5-8f5b-41e6-b07c-19c07229f813/content \


Medium article 42 gomoku : https://medium.com/@viniciuspetratti/how-we-made-an-ai-play-gomoku-5f4344d0b41 \
Heuristic for connect 4 : https://www.researchgate.net/publication/331552609_Research_on_Different_Heuristics_for_Minimax_Algorithm_Insight_from_Connect-4_Game \

TODO :  Test current implemented functions
        Add jumpLiveThree, broken open three .XX.X. / .X.XX., same as jLiveFour?
        Add jumpDeadFour, OXXX.X.  
        Add closedDeadFour OXXXXO ?



Ideas :
        Bonus for future move which creates forks ?
        Endpoint mask to avoid multicounting the same threat ?
        Cython/Numba for optimization ?
        Transpo table / Zobrist ?
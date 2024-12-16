import typing
import abc

from collections import deque

T = typing.TypeVar('T')
V = typing.TypeVar('V')

# class Pipeline[K,V]:
#     __slots__ = 'processes','work','done','out','callback'
#     def __init__(self,callback:typing.Optional[typing.Callable[[typing.Mapping[K,V]],typing.Any]]=None):
#         self.processes:list[PipelineProcess] = []
#         self.work:set[K] = set()
#         self.done:typing.Mapping[K,V] = dict()
#         if callback is None:
#             self.out:dict[K,typing.Any] = dict()
#         self.callback:typing.Callable[[typing.Mapping[K,V]],typing.Any] = callback or self.out.update
 
#     def addWork(self,work:typing.Iterable):
#         self.work.update(work)

#     def setProcesses(self,*processes:'PipelineProcess'):
#         self.processes = list(processes)

#     def update(self):
#         if not self.processes: return
#         #two steps:
#         # 1) Turtle Dependencies Down
#         # 2) Update Up and collect work done
#         a:typing.Collection = self.work
#         for process in reversed(self.processes):
#             process.addWork(a)
#             a = process.getNeeds()
#         if a:
#             raise RuntimeError(f'{self.processes[0].__class__.__name__} is the base process yet has external needs {self.work}')
#         else:
#             self.work.clear()
#         input = {}
#         for process in self.processes:
#             if input:
#                 process.addInput(input)
#             process.update()
#             input = process.getDone()
#         self.done = input
        
#         if self.done:
#             self.callback(self.done)


class Pipeline[K,V](typing.Protocol):
    callback:typing.Callable[[typing.Mapping[K,V]],typing.Any]
    def addMuchWork(self,work:typing.Iterable[K]): ...
    def addWork(self,one_work:K): ...
    def declareDependencies(self,key:K):'''For each key, set dependencies'''; ...
    def step(self,current:K) -> typing.Optional[V]: ...
    def updateDependencies(self):'''Update dependencies'''; ...
    def update(self): ...
         


class PipelineLayer[K,V](abc.ABC):
    '''Implementation of a one-shot Layer
     One-shot meaning: each pipeline update completes one "unit" of work that is sent out
    '''
    def __init__(self,callback:typing.Callable[[typing.Mapping[K,V]],typing.Any]|None=None):
        self.callback = callback or (lambda x:None)
        self.work:deque[K] = deque()
        

    def addMuchWork(self,work:typing.Iterable[K]):
        self.work.extend(work)
    
    def addWork(self,one_work:K):
        self.work.append(one_work)

    def declareDependencies(self,key:K):
        '''For each key, set dependencies'''

    @abc.abstractmethod
    def step(self,current:K) -> typing.Optional[V]: ...

    def updateDependencies(self):
        '''Update dependencies'''


    def update(self):
        if not self.work: return
        self.declareDependencies(self.work[0])
        self.updateDependencies()
        out = self.step(self.work[0])
        if out is not None:
            self.callback({self.work.popleft():out})


class PipelineLayerMultiStep[K,V](metaclass=abc.ABCMeta):
    '''Implementation of a multi-step Layer
     multi-step meaning: each "unit" of work that is sent out is computed over the course of multiple updates
    '''
    def __init__(self,callback:typing.Callable[[typing.Mapping[K,V]],typing.Any]|None=None):
        self.callback = callback or (lambda x:None)
        self.work:deque[K] = deque()
        self.current_key:K|None= None
        self.current_iter:typing.Iterator|None = None

    def addMuchWork(self,work:typing.Iterable[K]):
        self.work.extend(work)
    
    def addWork(self,one_work:K):
        self.work.append(one_work)

    def declareDependencies(self,key:K):
        '''For each key, set dependencies'''

    @abc.abstractmethod
    def step(self,current:K) -> typing.Generator[None,None,V]: ...


    def updateDependencies(self):
        '''Update dependencies'''


    def update(self):
        if self.current_key is None:
            if not self.work: return
            self.current_key = self.work.popleft()
            self.current = self.step(self.current_key)
            self.declareDependencies(self.work[0])
        self.updateDependencies()
        try:
            next(self.current)
        except StopIteration as err:
            self.callback({self.current_key:err.value})
            self.current_key = None



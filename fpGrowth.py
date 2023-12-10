import time

# Dosya yukleme ve Islem listelerini dondurme fonksiyonu
def dataLoad(filename):
    with open(filename) as f:
        content = f.readlines(); #icerik okundu
    content = [x.strip() for x in content];
    Transaction = [];
    for i in range(0, len(content)):
        Transaction.append(content[i].split());
    return Transaction;

# Ilk islemi frozenset'e donusturme fonksiyonu
#(set gibi ama donudurlmus ve degistirilemez bir kumeye donusur)
def createInit(dataset):
    retDict = {};
    for trans in dataset:
        retDict[frozenset(trans)] = 1;
    return retDict;

#Frequent Pattern Tree node sinifi..
class TreeNode:
    def __init__(self, nodeName,counter,parentNode):
        self.name = nodeName;
        self.count = counter;
        self.nodeLink = None;
        self.parent = parentNode;
        self.children = {};
        
    def incrCount(self, counter):
        self.count += counter;

#FP Tree icin header table ve sirali itemsetleri olusturma fonksiyonu
def createFPTree(dataset, minSupport):
    headerTable = {};
    for transaction in dataset:
        for item in transaction:
            headerTable[item] = headerTable.get(item,0) + dataset[transaction];
    for k in list(headerTable):
        if headerTable[k] < minSupport:
            del(headerTable[k]); #ignore, outlier

    freqItemset = set(headerTable.keys());

    if len(freqItemset) == 0:
        return None, None;
    #print("headerTable: " + str(headerTable));
    for k in headerTable:
        headerTable[k] = [headerTable[k], None];
 
    retTree = TreeNode('Null Set',1,None);
    for itemset,count in dataset.items():
        freqTrans = {};
        for item in itemset:
            if item in freqItemset:
                freqTrans[item] = headerTable[item][0];
        if len(freqTrans) > 0:
            #sirali itemsetleri islemlerden aldim
            orderedItemset = [v[0] for v in sorted(freqTrans.items(), key=lambda p: p[1], reverse=True)];
            #print("orderedItemset: " + str(orderedItemset));
            #FPTree guncellendi
            updateTree(orderedItemset, retTree, headerTable, count);
           
    return retTree, headerTable;

#Sirali itemsetleri kullanarak FP Tree olusturma fonksiyonu
def updateTree(itemset, FPTree, headerTable, count):
    if itemset[0] in FPTree.children:
        FPTree.children[itemset[0]].incrCount(count);
    else:
        FPTree.children[itemset[0]] = TreeNode(itemset[0], count, FPTree);
        if headerTable[itemset[0]][1] == None:
            headerTable[itemset[0]][1] = FPTree.children[itemset[0]];
        else:
            updateNodeLink(headerTable[itemset[0]][1], FPTree.children[itemset[0]]);

    if len(itemset) > 1:
        updateTree(itemset[1::], FPTree.children[itemset[0]], headerTable, count);

# FP Treedeki node linkini guncelleme fonksiyonu
def updateNodeLink(testNode, targetNode):
    while (testNode.nodeLink != None):
        testNode = testNode.nodeLink;
    testNode.nodeLink = targetNode;

#FP Tree caprazlama fonksiyonu
def FPTreeUpTransveral(leafNode, prefixPath):
 if leafNode.parent != None:
    prefixPath.append(leafNode.name);
    FPTreeUpTransveral(leafNode.parent, prefixPath);

#Pattern tabanlarini bulma fonksiyonu
def findPrefixPath(basePat, TreeNode):
 conditionalPatternBase = {};
 while TreeNode != None:
    prefixPath = [];
    FPTreeUpTransveral(TreeNode, prefixPath);
    if len(prefixPath) > 1:
        conditionalPatternBase[frozenset(prefixPath[1:])] = TreeNode.count;
    TreeNode = TreeNode.nodeLink;
    #print("conditionalPatternBase: " + str(conditionalPatternBase));
 return conditionalPatternBase;

# recursively conditional pattern tabani ve FP Tree mining yapma fonksiyonu
def MineTree(FPTree, headerTable, minSupport, prefix, freqItemset):
    bigL = [v[0] for v in sorted(headerTable.items(),key=lambda p: p[1][0])];
    for basePat in bigL:
        newFrequentset = prefix.copy();
        newFrequentset.add(basePat);
        #son frequent itemset listesine yeni frequent itemset ekledim
        freqItemset.append(newFrequentset);
        #item veya itemsetler icin butun conditional pattern tabanlarini aldim
        conditionalPatternBases = findPrefixPath(basePat, headerTable[basePat][1]);
        #conditional FP Tree yapmak icin FP Tree yapisini cagirdim
        conditionalFPTree, conditionalHeader = createFPTree(conditionalPatternBases,minSupport);
        #print("conditionalPatternBases: " + str(conditionalPatternBases));
        #print("freqItemset: " + str(freqItemset));
        if conditionalHeader != None:
            MineTree(conditionalFPTree, conditionalHeader, minSupport, newFrequentset, freqItemset);

#kullanicidan filename and minimum support(treshold) count aldim
print("Enter the filename:");
filename = input();
print("Enter the minimum support count:");
min_Support = int(input());

initSet = createInit(dataLoad(filename));
start = time.time();    # zaman hesaplandi
FPtree, headerTable = createFPTree(initSet, min_Support);

freqItemset = [];
# tum ferquent itemsetleri incelemek icin fonksiyonu cagirdim 
MineTree(FPtree, headerTable, min_Support, set([]), freqItemset);
end = time.time();

print("Time Taken is:");
print(end-start);
print("All frequent itemsets:");
print(freqItemset);

def compress(b:bytes) -> bytearray:
    if not b: return bytearray()
    codebook:dict[bytes,int] = {}
    compressed = bytearray()
    cb_len = codebook.__len__
    bpe = 1 #bytes per entry
    word_start = 0
    word_end = 1
    len_b = len(b)
    extend = compressed.extend
    append = compressed.append
    nullbytes = bytes(1)
    while word_end != len_b:
        if codebook.get(b[word_start:word_end]) is not None:
            word_end +=1
        else:
            len_ = cb_len()+1
            codebook[b[word_start:word_end]] = len_
            if word_end == 1+word_start:
                extend(nullbytes + b[word_start:word_end])
            else:
                extend(codebook[b[word_start:word_end-1]].to_bytes(bpe))
                append(b[word_end-1]) # enter the index of the compressed word into the stream
            word_start = word_end
            word_end = word_start+1
            if len_ == 0xFF or len_ == 0xFF_FF or len_ == 0xFF_FF_FF:
                bpe += 1
                nullbytes = bytes(bpe)
    if word_end == word_start+1:
        extend(nullbytes)
        extend(b[word_start:word_end])
    else:
        extend(codebook[b[word_start:word_end-1]].to_bytes(bpe))
        append(b[-1]) # enter the index of the compressed word into the stream
    return compressed


def decompress(b:bytes):
    codebook:dict[int,bytes] = {}
    bytes_per_word = 2
    i = 0
    uncompressed = bytearray()
    extend = uncompressed.extend
    cb_len = 0
    while i < b.__len__():
        word = b[i:i+bytes_per_word]
        entry = int.from_bytes(word[:-1],'big')
        letter =  word[-1:]
        if entry:
            letter = codebook[entry] + letter
        codebook[cb_len+1] = letter
        cb_len += 1
        extend(letter)

        i += bytes_per_word

        if (cb_len) in {0xFF, 0xFF_FF, 0xFF_FF_FF}:
            bytes_per_word += 1
        #if cb_len % 1000 == 0:
        #    print(f"{i*100/len(b):2.0f}%",end='\r')
        
    return uncompressed

def decompress_async(b:bytes):
    if b[:3] != b'lz1': return b
    b = b[3:]
    hundredth = max(0,len(b)//100)
    codebook:dict[int,bytes] = {}
    bytes_per_word = 2
    i = 0
    uncompressed = bytearray()
    extend = uncompressed.extend
    cb_len = 0
    b_len = b.__len__()
    while i < b_len:
        word = b[i:i+bytes_per_word]
        entry = int.from_bytes(word[:-1],'big')
        letter =  word[-1:]
        if entry:
            letter = codebook[entry] + letter
        codebook[cb_len+1] = letter
        cb_len += 1
        extend(letter)
        i += bytes_per_word
        if (cb_len) in {0xFF, 0xFF_FF, 0xFF_FF_FF}:
            bytes_per_word += 1
        if cb_len % hundredth == 0:
            yield i/len(b)
    return uncompressed


if __name__ == '__main__':
    test = b'''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras vestibulum eros nec facilisis commodo. Fusce tristique porta rhoncus. Ut rhoncus malesuada elit et suscipit. Suspendisse potenti. Sed mollis nunc et blandit tempor. Nulla feugiat quam sit amet tortor facilisis volutpat ac eu sapien. Maecenas semper diam nec odio egestas pulvinar. Maecenas vulputate erat vitae ante lacinia, in malesuada justo convallis. Sed et metus nec nunc molestie tristique et ut libero. Ut semper, lectus vitae dapibus convallis, risus magna volutpat odio, sit amet posuere nisi ante et libero. Duis ullamcorper lectus id neque interdum, id malesuada quam condimentum. Fusce vehicula condimentum nisi vitae tincidunt. Nam eget neque vel felis hendrerit interdum. Sed vel pretium turpis. Ut eu magna aliquam, porttitor massa eget, vehicula libero. Quisque pretium purus non urna blandit elementum. Nullam et magna velit. Pellentesque sem sem, fermentum vel neque nec, tempor viverra erat.Phasellus placerat libero at felis auctor, id ultrices neque pharetra. Aliquam vehicula nisl quis est condimentum, eu pretium massa suscipit. Etiam quis venenatis ipsum. Sed at lorem aliquam, rhoncus sapien et, condimentum quam. Etiam sed congue nunc, sit amet tincidunt diam. Fusce viverra felis at nisl congue pretium. Aliquam id velit ac ipsum hendrerit egestas sed vel orci.Donec consectetur, mi eget facilisis iaculis, nulla est faucibus lorem, ac accumsan lectus turpis vel mauris. Nulla cursus semper velit ac aliquet. Nulla vitae malesuada felis. Duis iaculis pulvinar mauris, nec porttitor est sodales quis. Ut quis purus at dui venenatis placerat eget in odio. Morbi augue lacus, imperdiet ut leo vitae, blandit gravida tellus. Pellentesque tortor ligula, vehicula ac pretium eu, sollicitudin et mauris. In a mi varius, luctus orci eu, porta diam. Fusce sollicitudin ac elit lacinia euismod. Sed accumsan vestibulum aliquam. Maecenas scelerisque elementum odio vel laoreet. Vestibulum id imperdiet ipsum. Ut quis mauris ex. Phasellus nec quam pharetra, molestie neque vitae, varius justo. Suspendisse ex enim, tristique ac fringilla vel, lobortis eu mauris. Vestibulum lobortis tortor sit amet purus laoreet blandit. Curabitur consectetur efficitur sem sit amet porta. Etiam sollicitudin euismod sapien, scelerisque sodales tellus bibendum eget. Sed condimentum tortor ante, mattis scelerisque purus lacinia nec. Nullam sodales massa eget enim elementum, vitae congue arcu feugiat. Proin volutpat sed arcu non tincidunt. Praesent rutrum nibh eu augue convallis fringilla. Maecenas eu augue euismod, molestie nisi in, tincidunt lacus. Nam imperdiet sollicitudin sem, ut dignissim nunc fermentum id. Nullam vulputate rutrum hendrerit. Praesent accumsan eget dui blandit laoreet. Integer eget tincidunt ipsum. Cras gravida leo at aliquet rhoncus. Aliquam viverra hendrerit massa auctor bibendum. Curabitur erat erat, egestas sit amet pretium vitae, lacinia a justo. Fusce porta turpis id aliquet consectetur. Proin pellentesque odio ligula, sed ullamcorper dolor feugiat eget. Vivamus non urna dictum, facilisis leo non, tempor metus. Praesent non mattis enim. Curabitur ut elementum eros. Praesent elementum dolor metus, vitae euismod nulla dictum ornare.Fusce malesuada ac ipsum non vehicula. Sed in efficitur ligula, in sodales metus. Duis bibendum sapien libero, quis tempor nisi lobortis non. Nulla a massa lectus. Donec vitae neque non sem pulvinar lobortis. Quisque gravida lacinia tempor. Vestibulum fermentum nibh sit amet nisl consequat, quis eleifend leo tincidunt. Nullam ligula magna, elementum vel tortor non, iaculis malesuada nisl. Curabitur blandit auctor nulla, ac ornare dolor scelerisque vel. Donec et convallis diam. Proin lobortis, ante ac volutpat iaculis, leo erat ultrices ante, at hendrerit diam augue ac leo. Pellentesque venenatis elementum sapien, quis bibendum ipsum suscipit ac. Pellentesque non ante a est pellentesque eleifend iaculis at ligula. Duis congue purus iaculis sem feugiat, consectetur dictum purus mollis. Donec lacinia semper orci nec euismod. Nulla pellentesque pellentesque est sit amet finibus. Nullam luctus tortor id justo posuere tincidunt id vel elit. Proin quam augue, efficitur nec dignissim ut, fringilla lobortis ipsum. Cras accumsan hendrerit quam et laoreet. Curabitur quis ornare metus. Donec at massa eget lacus molestie scelerisque. Integer ultrices placerat ligula, nec condimentum ante. Duis quis ultrices dui. Sed efficitur eu turpis ut dictum. Vestibulum ornare, est at finibus elementum, velit mi pellentesque justo, a vehicula orci purus a nibh. Morbi quis enim nec erat tempor varius. Nunc dictum magna nec efficitur faucibus. Cras nec enim molestie, sollicitudin turpis eget, dictum tellus. Donec nec ipsum vitae libero tincidunt pulvinar venenatis ut ex. Suspendisse neque est, malesuada id ultrices eget, mattis non tortor. Proin vitae tristique lacus, sed fringilla diam. Pellentesque felis velit, consequat eu velit at, vulputate eleifend odio. Aliquam sed enim est. Nullam sed turpis mattis urna pretium efficitur vel vel quam. Phasellus molestie, nulla tempus consectetur vehicula, nunc leo sodales sem, a tempus ante mi a lectus. Mauris at turpis vitae velit semper lobortis. Pellentesque imperdiet auctor elit, in porta mauris eleifend non. Proin enim augue, fermentum sit amet ultrices ut, porta eget arcu. Duis viverra justo vel augue lobortis, vitae facilisis urna pellentesque. Fusce cursus dignissim vestibulum. Donec vitae tellus porttitor, sagittis leo ac, semper nibh. Nam aliquet orci in eros aliquet accumsan. Cras suscipit tellus a condimentum maximus. Suspendisse mi justo, venenatis sed tortor sed, varius consectetur lacus. Aliquam varius quam quis leo fermentum cursus. Nullam tempus placerat nisi quis dignissim. Quisque luctus erat eget tempor viverra. Proin nec consequat arcu. Phasellus sodales imperdiet interdum. Aliquam id posuere dolor, eu auctor nulla. Duis scelerisque neque non arcu lobortis posuere. Curabitur velit felis, dictum sed pulvinar ac, tristique a lectus. Sed egestas euismod iaculis. Morbi nisl turpis, porta lobortis magna vitae, hendrerit pharetra nibh. Etiam consequat mauris ut eros malesuada, vitae feugiat turpis efficitur. Aenean quis lobortis orci. Curabitur eu nulla maximus, facilisis enim et, pulvinar elit. Curabitur consequat quis massa in condimentum. Morbi sit amet luctus nulla. Suspendisse a pellentesque turpis. Nam blandit arcu ligula, non ultrices lorem dapibus et. Sed mattis lorem placerat sodales feugiat. Fusce molestie eu velit ac tempor. Nam sit amet mi feugiat velit tincidunt elementum ut et quam. Pellentesque ultrices justo non rutrum accumsan. Morbi ac aliquam odio, eget ornare lacus. Curabitur sed mattis ligula, sit amet aliquet purus. Suspendisse tortor lectus, elementum sit amet ligula molestie, tristique euismod diam. Integer sit amet metus eu risus scelerisque sollicitudin. Sed rutrum congue orci. Aliquam id urna consequat, blandit leo sit amet, finibus nisl. Nullam a lorem a ante euismod tincidunt. Cras neque felis, facilisis vitae viverra id, commodo a odio. Nulla eget elementum arcu. Maecenas posuere ex vel viverra placerat. Cras diam est, ornare eu ante ac, dictum fermentum tortor. Sed venenatis augue nec dictum dignissim. Vestibulum suscipit in leo eu dapibus. Integer in nisl nisi. Maecenas accumsan nulla eget odio molestie scelerisque. Proin varius metus nec velit auctor, vel commodo eros porta. Donec gravida pulvinar facilisis. Donec luctus elementum varius. Ut pulvinar ex nisi. Proin auctor posuere urna vitae rhoncus. Morbi et libero elementum, sodales sem vitae, egestas purus. Integer sodales, erat id dapibus cursus, ligula felis luctus nunc, vitae efficitur dui ante quis orci. Quisque eu condimentum neque. Donec venenatis eros at imperdiet imperdiet. Aenean ut purus in diam ultrices consectetur. Nulla facilisi. Phasellus vel risus in lectus semper bibendum dictum sed quam. Ut at pellentesque ligula. Donec dignissim aliquet enim, et auctor velit finibus vel. Nam egestas ipsum sed mauris blandit, quis ultrices metus mattis. Pellentesque a augue porta, pulvinar ipsum eget, tristique justo. Etiam maximus ipsum non aliquet gravida. Nulla imperdiet mollis ultrices. Nunc nec aliquam orci. Cras vitae cursus metus. Proin tincidunt et eros id finibus. Mauris sed sapien elit. Pellentesque aliquam tempor tortor, nec dapibus mauris ullamcorper nec. Etiam hendrerit pharetra metus, quis vehicula nulla iaculis a. Duis et nulla neque. Integer dapibus blandit eleifend. Aliquam dapibus consequat risus non suscipit. Cras eleifend leo in lobortis fermentum. Aenean elit nisi, molestie in semper in, consectetur vel enim. Praesent pulvinar diam ex, sed efficitur mauris feugiat vel. Ut feugiat ex libero, vel consequat lorem molestie in. Ut gravida ut nisi id rhoncus. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Phasellus vitae luctus lectus. Aenean tristique nulla eget faucibus eleifend. Quisque maximus magna mollis, efficitur erat quis, eleifend mauris. In suscipit ultrices commodo. Fusce scelerisque ullamcorper risus ac pulvinar. Vestibulum tincidunt felis bibendum leo ultrices ullamcorper. Etiam mattis elit enim, id venenatis leo scelerisque non. Aenean sed ultrices ante. Aenean posuere, dolor at facilisis lacinia, arcu mi suscipit velit, quis dapibus diam enim et lectus.Mauris urna mauris, lacinia sed risus eget, porta tincidunt dui. Sed diam est, tincidunt at hendrerit id, laoreet eget ante. Sed consectetur facilisis lorem nec bibendum. Aliquam erat volutpat. Donec semper ultricies felis, quis porta leo placerat ultricies. Morbi ac maximus lacus. Fusce metus velit, consequat at laoreet ac, dignissim id ipsum. Sed dui massa, egestas ac libero id, ultrices porta magna. Nullam pellentesque turpis sed neque ultricies interdum. Aliquam erat volutpat. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Vestibulum imperdiet vulputate faucibus. Suspendisse sed tincidunt mauris. Quisque convallis finibus congue. Integer tristique scelerisque tristique. Mauris dignissim aliquam maximus. Suspendisse condimentum magna a tempus aliquam. Maecenas suscipit ligula ac semper sollicitudin. Nam fermentum massa a lectus ultrices, ac euismod nisi placerat. Praesent non justo eget est cursus varius nec vel odio. Phasellus pretium ante orci, vel finibus arcu tincidunt a. Donec laoreet eros tortor, id scelerisque magna laoreet eget. Cras nunc lacus, pulvinar nec ex quis, interdum suscipit lectus. Etiam vitae purus non massa dictum imperdiet a sit amet nibh. Maecenas consectetur malesuada lacus, sit amet malesuada nunc condimentum nec. Maecenas mattis ante ut magna convallis ornare. Etiam ornare orci sit amet euismod consequat. Aenean vitae placerat tellus. Sed justo enim, vulputate id pretium eget, ullamcorper ut ante. Aenean pulvinar odio vitae commodo venenatis. Praesent congue ipsum tortor, non varius nulla pretium sed. Nam blandit tempor posuere.'''
    right = 0
    wrong = 0
    wrongs:list[int] = []
    for i in range(len(test)//2,len(test),10):
        print(i,end='\r')
        t = test[:i]
        if decompress(compress(t))==t:
            right += 1
        else:
            wrong += 1
            wrongs.append(i)
    
    print('Compression Ratio:',len(compress(test))/len(test))
    b = len(test)
    from timeit import timeit
    time = timeit('compress(test)',number=1_000,globals=globals())
    
    print(f'Compression Speed: {(b/(time*1000)):.2f} MB/s')

    print('Correct | Incorrect:',right,'|',wrong)
    if wrong:
        print('Incorrect Indices:',wrongs)
 

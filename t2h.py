import re,base64,sys

VERS = "0.6" # 20110206-201100
DTME = str(__import__("time").strftime("%Y.%m.%d %H:%M:%S"))

CH_EP = '0-9A-Za-z?!'
CH_EK = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz?!'
CH_1C = ':.-+=~/*&<>°^`"\'' #$%!?@&\_,;|
CH_1K = 'cdmpetsxnlgoubqa'             # 16+6=22 done: abcdeglmnopqstux(ijkrvw), 4 left: fhyz
CH_2K = 'ABCDEFGHIJKLMNOPQRSTUVWX'     # 24 *64 = 1536         YZ left --> CH_4K,CH_XX
CH_3K = '01234567ijkrvw89'             # 16 *64*64 = 65536
CH_4K = 'Y'                            # 1  *64*64*64 = 262144 (0..#3FFFF)
CH_EN = len(CH_EK); assert CH_EN==64
CH_1N = len(CH_1K); assert CH_1N==16
CH_2N = len(CH_2K); assert CH_2N==24
CH_3N = len(CH_3K); assert CH_3N==16
CH_2NEN = CH_2N*CH_EN
CH_ENEN = CH_EN*CH_EN
CH_ENNN = CH_EN*CH_EN*CH_EN
CH_ZZ = '`Z'
CH_ZA1 = CH_ZZ+"KX"
CH_ZA2 = CH_ZZ+"KY"
CH_ZIMG= CH_ZZ+"GX"

def char_to_esc( c ):
  u = ord(c)
  if c==' ': return 'b'          # `blank --> `b (which will be ` in output)
  if u<255 and c in CH_1C:       # 16: K
    return CH_1K[CH_1C.find(c)]
  if u<CH_2NEN:                  # 23: LA
    u,v = divmod(u,CH_EN)
    return CH_2K[u]+CH_EK[v]
  assert u<CH_3N*CH_ENEN # <64K  # 16: MAA
  u,v = divmod(u,CH_ENEN)
  v,w = divmod(v,CH_EN)
  return CH_3K[u]+CH_EK[v]+CH_EK[w]

def esc1_to_char( c ): return CH_1C[CH_1K.find(c)]
def esc2_to_char( c ): return chr( CH_2K.find(c[0])*CH_EN + CH_EK.find(c[1]) ) #+"<!"+c[0]+c[1]+">"
def esc3_to_char( c ): return chr( CH_3K.find(c[0])*CH_ENEN + CH_EK.find(c[1])*CH_EN + CH_EK.find(c[2]) ) #+"<!"+c[0]+c[1]+c[2]+">"

escape_line_p = re.compile( '`([^'+CH_1K+CH_2K+CH_3K+'])' )
def escape_line( s ):
  return escape_line_p.sub( lambda m: '`'+char_to_esc(m.group(1)), s )

unescape_line_p1 = re.compile( '`(['+CH_1K+'])' )
unescape_line_p2 = re.compile( '`(['+CH_2K+']['+CH_EP+'])' )
unescape_line_p3 = re.compile( '`(['+CH_3K+']['+CH_EP+']['+CH_EP+'])' )
def unescape_text( s ):
  t = unescape_line_p3.sub( lambda m: esc3_to_char(m.group(1)), s )
  t = unescape_line_p2.sub( lambda m: esc2_to_char(m.group(1)), t )
  t = unescape_line_p1.sub( lambda m: esc1_to_char(m.group(1)), t )
  # leave CH_2K ~CH_EP, CH_3K ~CH_EP, CH_3K CH_EP ~CH_EP
  return t

# for testing mainly
if len(sys.argv)==2 and sys.argv[1][0]=="`":
  c = unescape_text(sys.argv[1]); print( ord(c) );
  try: print(c)
  except: print("cant't print char here; hex:","%X"%ord(c))
  sys.exit(0)
if len(sys.argv)==2 and sys.argv[1].isdigit():
  print( int(sys.argv[1]), '`'+char_to_esc(chr(int(sys.argv[1]))) )
  sys.exit(0)
if len(sys.argv)==3 and sys.argv[1].isdigit() and sys.argv[2].isdigit():
  o = open("chars.txt","wt",encoding="utf-8")
  c = 1
  for i in range( int(sys.argv[1]), int(sys.argv[2])+1 ):
    if i>=0x590 and i<0x900: continue # `WG..0a0
    print( chr(i), i, '`'+char_to_esc(chr(i)), file=o, end=((c%5==0)and"\n"or"      ") ); c+=1
  o.close()
  print( 'see chars.txt' )
  sys.exit(0)

def encode64(s):
  """encode unicode string to CH_EP set, return unicode string, length will increase 1.348x"""
  b = base64.b64encode(s.encode("utf-8"),b"?!")
  if b.endswith(b'='): b=b[:-1]
  if b.endswith(b'='): return b[:-1].decode("utf-8")
  return b.decode("utf-8")

def decode64(b):
  """decode unicode CH_EP string, return original string"""
  b = b.encode("utf-8"); m = len(b)%4
  if m==2: t = base64.b64decode(b+b"==",b"?!")
  elif m==3: t = base64.b64decode(b+b"=",b"?!")
  else: t = base64.b64decode(b,b"?!")
  return t.decode("utf-8")

def remove_comment( s ):
  if s.startswith( ".." ): return "",True
  t = re.sub( " +\.\..*$", "", s )
  return t,t!=s

def remove_formatting( s ):
  m = re.search( "(^|(?: +))([.:][-+0-9.:].*)$", s )
  if m: return s[:m.start(0)],m.group(2).rstrip()
  return s,""

def encode_url( m ):
  urls.append( m.group(0) )
  return "%s%04d" % (CH_ZA1,len(urls)-1)

def encode_url2( m ):
  #print("e2",m.group(1))
  urls.append( m.group(2) )
  return "%s%04d%s%s" % (CH_ZA2,len(urls)-1,encode64(m.group(1)),CH_ZA2)

def encode_image_url( m ):
  urls.append( m.group(1) )
  return "%s%04d" % (CH_ZIMG,len(urls)-1)

def decode_url( m ):
  n = int(m.group(1),10)
  return "<a href=\"%s\">%s</a>" % (urls[n],urls[n])

def decode_url2( m ):
  #print("d2",m.group(2))
  n = int(m.group(1),10)
  return "<a href=\"%s\">%s</a>" % (urls[n],decode64(m.group(2)))

def decode_image_url( m ):
  n = int(m.group(1),10)
  return "<img src=\"%s\">" % (urls[n])

urls = [] # url, accessed by index

def text2html( t ):
    # urls: links http://wwwww including // ? & etc --> CH_ZA1+nnnnn
    #       links <<..>> including // ? & etc       --> CH_ZA2+nnnnnuuuuuuuu+CH_ZA2
    #       images [[..]]                           --> CH_ZIMG+nnnnn
    # < > &    --> &lt; &gt; &amp;
    # ., .,, .,,, etc    --> &nbsp;
    # **..** //..// --..-- ++..++ ^^..^^ ~~..~~      --> html <..>....</..>
    assert CH_ZA1 not in t and CH_ZA2 not in t and CH_ZIMG not in t
    u = re.sub( "\[\[(.+?)\]\]", encode_image_url, t )
    u = re.sub( "<<(.+?)>>\s\((.+?)\)", encode_url2, u, flags=re.I )
    u = re.sub( "((?:http(?:s)?|ftp|file)://\S+)", encode_url, u, flags=re.I )
# ##label      a name
# @@span@@     highlited, or used for styling
    # no html yet
    v = u.replace( "&", "&amp;" ).replace( "<", "&lt;" ).replace( ">", "&gt;" )
    v = v.replace( " // ","<br/>" )
    v = re.sub( "//(\S(?:.*?\S)??)//", "<i>\\1</i>", v )
    v = re.sub( "\*\*(\S(?:.*?\S)??)\*\*", "<b>\\1</b>", v )
    v = re.sub( "\+\+(\S(?:.*?\S)??)\+\+", "<ins>\\1</ins>", v )
    v = re.sub( "--(\S(?:.*?\S)??)--", "<del>\\1</del>", v )
    v = re.sub( "''(\S(?:.*?\S)??)''", "<tt>\\1</tt>", v )
    v = re.sub( "~~(\S(?:.*?\S)??)~~", "<sub>\\1</sub>", v )
    v = re.sub( "\^\^(\S(?:.*?\S)??)\^\^", "<sup>\\1</sup>", v )
    v = v.replace( " (C) ", " &copy; " ).replace( " --", "&nbsp;&mdash;" ).replace( "(TM)", "&trade;" )
    v = v.replace( chr(160), "&nbsp;" )
    v = re.sub( "\.(,+)", lambda m: "&nbsp;"*len(m.group(1)), v )
    v = unescape_text( v )
    v = re.sub( CH_ZA2+"(\\d\\d\\d\\d)(.*?)"+CH_ZA2, decode_url2, v )
    v = re.sub( CH_ZA1+"(\\d\\d\\d\\d)", decode_url, v )
    v = re.sub( CH_ZIMG+"(\\d\\d\\d\\d)", decode_image_url, v )
    return v

def printout_toc( o, toc ):
  for lvl,h_id,text in toc:
    assert lvl>=2
    print( 3*(lvl-2)*"&nbsp;" + "<a href=\"#%s\">"%h_id + text + "</a><br/>", file=o )

def printout_page( o, title, style, page ):
  print( "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'/>", file=o )
  print( "<!-- Generated %s with T2H.py version %s -->" % (DTME,VERS), file=o )
  print( "<title>%s</title>\n<style>%s</style>\n</head>\n<body>" % (title,style), file=o )
  # TOC
  print( "<div class=TOC>", file=o ) # just sample. should be subst for :: etc
  printout_toc( o, toc )
  print( "</div>", file=o )
  # body divs
  for div in page:
    tag,attrs,text = div
    if tag=="hr":
      print( "<hr/>", file=o )
    elif tag=="h1":
      print( "<h1>%s</h1>"%title, file=o )
    elif tag in ("h2","h3","h4","h5","h6"):
      h_id = attrs['hdrname']
      print( "<%s><a name=\"%s\"/>%s</%s>"%(tag,h_id,text,tag), file=o )
    else:
      print( "<%s>"%tag, file=o )
      print( text, file=o )
      print( "</%s>"%tag, file=o )
  print( "</body>\n</html>", file=o )

title = ""
style = ".TOC{border:1px solid black;padding:0.5em 1em;width:80%;}tt{background-color:#DDD;"
page = [] # divs like ["p",{"attr":"value"},"text-of-div"]

toc = [] # (LEVEL,LABEL,TEXT),...
finished = False
in_text = False
line_nr = 0
text = ""

def finish_block( t, tag, line_nr=0, attrs=None ):
  global finished, page
  if not attrs: attrs = {}
  if line_nr == 1 and re.match( "---+\s*", t ):
    page.append( ["hr",attrs,""] )
  elif line_nr == 1 and re.match( "===+\s*", t ):
    finished = True
  else:
    assert not t.startswith(' ')
    t = text2html( t.rstrip() )
    page.append( [tag,attrs,t] )

def process_line( line ):
  global text, in_text, line_nr, toc, title
  t = escape_line( line.rstrip().replace("\t"," ").replace("\v"," ") )
  b = len(t); u = t.lstrip(); b -= len(u) # count leading blanks --> b
  u,comment_was_removed = remove_comment( u )
  u,fmt = remove_formatting( u ) # formats are in fmt
  if fmt: print( fmt )
  if len(u)==0:
    if comment_was_removed and len(fmt)==0:
      return
    if in_text:
      finish_block( text, "p", line_nr )
      in_text = False
      text = ""
    return
  if not in_text: # and some text in u -- start text,in_text
    line_nr = 1
    text = u + " "
    if len(u)>3 and (u.startswith("== ") or u.startswith("-- ")):
      lvl = u[0]=='=' and 4 or 5
      h_num = len(toc)
      h_id = "TOC%08d" % h_num
      text = re.sub( "[-=\s]+$", "", text[3:] ) # remove trailing -- and ==
      toc.append( (lvl,h_id,text) )
      finish_block( text, "h%s"%lvl, line_nr, {'hdrname':h_id} )
      in_text = False
    else:
      in_text = True
  else: # add to in_text
    line_nr += 1
    if re.match("==+$",u) or re.match("--+$",u): # h2 or h3
      if len(title)==0: # first header - h1
        title = text.rstrip()
        finish_block( title, "h1" )
      else:
        lvl = u[0]=='=' and 2 or 3
        h_num = len(toc)
        h_id = "TOC%08d" % h_num
        text = text.rstrip()
        toc.append( (lvl,h_id,text) )
        finish_block( text, "h%s"%lvl, line_nr, {'hdrname':h_id} )
      in_text = False
      text = ""
    else:
      text += u + " "

fname = "t2h.txt" # sys.argv[1]

f = open(fname,"rt",encoding="utf-8")
for line in f:
  process_line( line )
  if finished: break
if in_text:
  finish_block( text, "p", line_nr )
f.close()

o = open(fname+".htm","wt",encoding="utf-8")
printout_page( o, title, style, page )
o.close()

print("-----")
for i,u in enumerate(urls):
  print(i,u)


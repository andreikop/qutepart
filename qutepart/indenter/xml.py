
class IndenterXml(IndenterNormal):
    """TODO implement
    """
    def computeIndent(self, block, char):
        """Compute indent for the block
        """
        prevLineString = self._prevNonEmptyLineText(block)
        
        lineString = block.text()
        
        alignOnly = char == ''
        
        if alignOnly:
            # XML might be all in one line, in which case we want to break that up.
            tokens = re.split('/>\s*</')

            if len(tokens) > 1:
                
                prevIndent = self._lineIndent(prevLineString)
                
                for index, newLine in enumerate(tokens):
                    if index > 0:
                        newLine = '<' + newLine
                    
                    if index < len(tokens) - 1:
                        newLine = newLine + '>'
    
                    re.match('^\s*<\/', newLine):
                        char = '/'
                    elif re.match('\>[^<>]*$', newLine):
                        char = '>'
                    else
                        char = '\n'
                    
                    indentation = self.processChar(newLine, prevLineString, char)
                    newLine = indentation + newLine
                    
                    tokens[index] = newLine
                    prevLineString = newLine;
                    
                    block = block.next()
                
                print '\n'.join(tokens)
                print oldLine
            
                qpart.lines[block.blockNumber()] =  '\n'.join(tokens)
                return prevIndent
            else:
                if re.match('^\s*<\/', lineString):
                    char = '/'
                elif re.match('\>[^<>]*$/', lineString):
                    char = '>'
                else:
                    char = '\n'
    
        print block.blockNumber()
        print lineString
        print prevLineString
        print char
        return processChar(lineString, prevLineString, char)
    }
    
    def processChar(lineString, prevLineString, char):
        prevIndent = self._lineIndent(prevLineString)
        if char == '/':
            if not re.match('^\s*<\/', lineString):
                # might happen when we have something like <foo bar="asdf/ycxv">
                # don't change indentation then
                return self._lineIndent(lineString)

            if not re.match('<[^\/][^>]*[^\/]>[^<>]*$', prevLineString):
                # decrease indent when we write </ and prior line did not start a tag
                return self._removeIndent(prevIndent)
        elif char == '>':
            # increase indent width when we write <...> or <.../> but not </...>
            # and the prior line didn't close a tag
            if re.match('^<(\?xml|!DOCTYPE)', prevLineString):
                return ''
            elif re.match('^\s*<\/', lineString):
                #closing tag, decrease indentation when previous didn't open a tag
                if re.match('<[^\/][^>]*[^\/]>[^<>]*$', prevLineString):
                    # keep indent when prev line opened a tag
                    return prevIndent;
                else:
                    return self._removeIndent(prevIndent)
            elif re.match('<([\/!][^>]+|[^>]+\/)>\s*$', prevLineString):
                # keep indent when prev line closed a tag or was empty or a comment
                return prevIndent
            
            return prevIndent + self._indentText()
        elif char == '\n':
            if re.match('^<(\?xml|!DOCTYPE)', prevLineString):
                return ''
            elif re.match('<[^\/!][^>]*[^\/]>[^<>]*$', prevLineString):
                # increase indent when prev line opened a tag (but not for comments)
                return prevIndent + self._indentText()
    
        return prevIndent

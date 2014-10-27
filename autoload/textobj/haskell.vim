if !has('python')
    echomsg "Warning: textobj-haskell requires python"
    finish
endif

function! textobj#haskell#select_i()
    python select_haskell_block(vim.current.buffer, vim.current.window.cursor[0], False)

    let start_position = g:haskell_textobj_ret[0]
    let end_position = g:haskell_textobj_ret[1]
    return ['v', start_position, end_position]
endfunction

function! textobj#haskell#select_a()
    python select_haskell_block(vim.current.buffer, vim.current.window.cursor[0], True)

    let start_position = g:haskell_textobj_ret[0]
    let end_position = g:haskell_textobj_ret[1]
    return ['v', start_position, end_position]
endfunction

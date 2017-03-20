function imatlab_export_png()

  setenv('IMATLAB_EXPORT_FIG', func2str(@(h) eval([ ...
      'print(h, [tempname(''.''), ''.png''], ''-dpng'')', ...
      'close(h);'])));

end

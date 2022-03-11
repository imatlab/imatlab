# fix and enhance
- [x] CJK character display CORRECTLY now! 2022-3-9
- [x] use `plotly_matlab` to `_send_display_data` into jupyter notebook like `plotly.py`, which are three layers for `outputs.data`, such as `"application/vnd.plotly.v1+json": {json_compatible_fig_dict}`, `"image/png":"base64"` and `"text/html":"plotly_fig_html"`. see: [dennischancs/plotly_matlab](https://github.com/dennischancs/imatlab/tree/dennischancs-patch-1) ![](https://images.weserv.nl?url=https://raw.githubusercontent.com/dennischancs/pic/main/img/202203120246485.png)


## Install
```bash
pip install git+https://github.com/dennischancs/imatlab@dennischancs-patch-1  # from Github
python -mimatlab install --user
```

enable `fig2plotly` option  see: [dennischancs/plotly_matlab](https://github.com/dennischancs/plotly_matlab)

## Usage 

```matlab
%% one mothed to insert a matlab static figure as a cell to ipynb file
%imatlab_export_fig('print-svg')  % `imatlab_export_fig()` should put it first to prevent matlab_figure windows popup

%% one mothed to insert a plotly figure as a cell to ipynb file
imatlab_export_fig('fig2plotly')


plot(1:10,2:11);
title('测试fig2plotly');
filename = ['测试fig2plotly'];


%% one mothed to convert plotly figure to static image with png/jpg/webp/svg/pdf formats
% use `write_image.m` (recommend)
%write_image(gcf,'imageFormat','png','saveFile',false)

%% two mothed to export plotly figure with .html format
%1: use `write_html.m` (recommend)
%write_html(gcf)
%2: use `plotlyoffline.m`
%fig2plotly(gcf, 'filename', filename, 'offline', true, 'open', true);
```


## [More](./README.rst)
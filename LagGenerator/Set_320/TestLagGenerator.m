global order
global orderLag

numgood=0;
tries=10000;
for i=1:tries
    %good = CreateOrder_AllShort();
    good = CreateOrder_320();
    numgood = numgood + good;
    if good
        csvwrite(sprintf('order_%d.txt',numgood),[order orderLag])
    end
     if numgood == 5
         break
    end
end

numgood/tries

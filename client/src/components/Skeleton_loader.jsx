import React from 'react'

function Skeleton_loader() {
  return (
    <div class="mt-2 mx-auto bg-green-00 w-[50%]">
          <div class="animate-pulse w-[90%] flex bg-red-00">
            <div class="flex-1 space-y-6 py-1">
              <div class="h-2 bg-slate-700 rounded"></div>
              <div class="space-y-3">
                <div class="grid grid-cols-3 gap-4">
                  <div class="h-2 bg-slate-700 rounded col-span-2"></div>
                  <div class="h-2 bg-slate-700 rounded col-span-1"></div>
                </div>
                <div class="h-2 bg-slate-700 rounded"></div>
              </div>
            </div>
          </div>
        </div>
  )
}

export default Skeleton_loader
